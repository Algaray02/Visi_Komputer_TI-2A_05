import torch
from ultralytics import YOLO
import os
import psutil
import time
import subprocess
import threading
from pathlib import Path

class GPUMonitor:
    """Monitor GPU temperature and utilization"""
    def __init__(self, max_temp=70, target_util=85):
        self.max_temp = max_temp
        self.target_util = target_util
        self.monitoring = False
        
    def get_gpu_stats(self):
        """Get current GPU stats"""
        try:
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=temperature.gpu,utilization.gpu', 
                 '--format=csv,noheader,nounits'],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                temp, util = result.stdout.strip().split(',')
                return int(temp), int(util)
        except:
            pass
        return None, None
    
    def print_stats(self):
        """Print GPU stats with colors"""
        temp, util = self.get_gpu_stats()
        if temp is not None:
            temp_icon = "🔥" if temp > self.max_temp else "🟢" if temp < 65 else "🟡"
            util_icon = "🔴" if util > 95 else "🟡" if util > 85 else "🟢"
            print(f"\r{temp_icon} {temp}°C | {util_icon} {util}% GPU | Target: {self.target_util}%", end="", flush=True)

def check_system_health():
    """Check system resources"""
    print("\n" + "="*60)
    print("🔍 SYSTEM HEALTH CHECK")
    print("="*60)
    
    # CPU
    cpu_percent = psutil.cpu_percent(interval=1)
    print(f"💻 CPU Usage: {cpu_percent}%")
    
    # RAM
    ram = psutil.virtual_memory()
    print(f"🧠 RAM: {ram.percent}% ({ram.used/1024**3:.1f}GB / {ram.total/1024**3:.1f}GB)")
    print(f"   Available: {ram.available/1024**3:.1f}GB")
    
    if ram.percent > 90:
        print("⚠️ WARNING: RAM > 90%! May cause slowdown.")
    
    # Disk
    disk = psutil.disk_usage('/')
    print(f"💾 Disk: {disk.percent}% ({disk.free/1024**3:.1f}GB free)")
    
    # GPU
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        vram = torch.cuda.get_device_properties(0).total_memory / 1024**3
        print(f"🎮 GPU: {gpu_name}")
        print(f"   VRAM: {vram:.2f}GB")
        
        monitor = GPUMonitor()
        temp, util = monitor.get_gpu_stats()
        if temp:
            print(f"   Current: {temp}°C, {util}% utilization")
    
    print("="*60)
    
    # Recommendations
    if ram.percent > 85:
        print("\n💡 TIP: Close other applications to free RAM")
    if cpu_percent > 90:
        print("💡 TIP: High CPU usage detected")
    
    return ram.available

def find_last_checkpoint():
    """Find latest checkpoint"""
    checkpoints = []
    results_dir = Path('./results')
    
    if results_dir.exists():
        for project in results_dir.iterdir():
            if project.is_dir():
                weights_dir = project / 'weights'
                if weights_dir.exists():
                    last_pt = weights_dir / 'last.pt'
                    if last_pt.exists():
                        mtime = last_pt.stat().st_mtime
                        checkpoints.append((last_pt, mtime, project.name))
    
    if checkpoints:
        checkpoints.sort(key=lambda x: x[1], reverse=True)
        return checkpoints[0][0], checkpoints[0][2]
    
    return None, None

def get_training_config(mode, vram_gb, ram_available_gb, use_cache=True):
    """
    Get training configuration based on mode
    mode: 'full', 'balanced', 'efficient', 'minimal'
    """
    configs = {
        'full': {
            'name': '🔥 Full Performance',
            'batch': 12 if vram_gb >= 4 else 8,
            'workers': 4,
            'target_gpu': 95,
            'cache': use_cache and ram_available_gb > 8,
            'save_period': 10,
            'patience': 10,
            'description': 'Maximum speed, may run hot (70-75°C)'
        },
        'balanced': {
            'name': '⚖️ Balanced',
            'batch': 10 if vram_gb >= 4 else 6,
            'workers': 3,
            'target_gpu': 85,
            'cache': use_cache and ram_available_gb > 8,
            'save_period': 8,
            'patience': 12,
            'description': 'Good speed, stable temp (60-68°C) - RECOMMENDED'
        },
        'efficient': {
            'name': '❄️ Efficient',
            'batch': 8 if vram_gb >= 4 else 4,
            'workers': 2,
            'target_gpu': 80,
            'cache': use_cache and ram_available_gb > 6,
            'save_period': 6,
            'patience': 15,
            'description': 'Cool & stable, good for laptops (55-62°C)'
        },
        'minimal': {
            'name': '🛡️ Minimal',
            'batch': 4,
            'workers': 1,
            'target_gpu': 75,
            'cache': False,
            'save_period': 5,
            'patience': 20,
            'description': 'Ultra-safe, lowest resource usage (50-58°C)'
        }
    }
    
    return configs.get(mode, configs['balanced'])

def train_with_config(config, is_resume=False, checkpoint_path=None):
    """
    Train with given configuration
    """
    print("\n" + "="*60)
    print(f"🚀 TRAINING CONFIGURATION: {config['name']}")
    print("="*60)
    print(f"📦 Batch Size: {config['batch']}")
    print(f"👷 Workers: {config['workers']}")
    print(f"🎯 Target GPU: {config['target_gpu']}%")
    print(f"💾 Cache: {'Yes (RAM)' if config['cache'] else 'No (Disk)'}")
    print(f"💾 Save Period: Every {config['save_period']} epochs")
    print(f"⏸️ Patience: {config['patience']} epochs")
    print(f"📝 {config['description']}")
    print("="*60 + "\n")
    
    # GPU Monitoring
    monitor = GPUMonitor(max_temp=70, target_util=config['target_gpu'])
    monitor.monitoring = True
    
    def monitor_gpu():
        while monitor.monitoring:
            monitor.print_stats()
            time.sleep(2)
    
    monitor_thread = threading.Thread(target=monitor_gpu, daemon=True)
    monitor_thread.start()
    
    try:
        if is_resume and checkpoint_path:
            print(f"🔄 Resuming from: {checkpoint_path}\n")
            model = YOLO(str(checkpoint_path))
            
            results = model.train(
                resume=True,
                
                # Apply new config
                batch=config['batch'],
                workers=config['workers'],
                cache=config['cache'],
                patience=config['patience'],
                save_period=config['save_period'],
                
                amp=True,
                rect=False,
                verbose=True,
            )
        else:
            print(f"🆕 Starting new training\n")
            model = YOLO('yolo11n.pt')
            
            results = model.train(
                # Dataset
                data='./datasets/detect-helmet/data.yaml',
                
                # Duration
                epochs=50,
                patience=config['patience'],
                
                # Performance settings
                batch=config['batch'],
                workers=config['workers'],
                cache=config['cache'],
                
                # Image
                imgsz=640,
                
                # Device
                device=0,
                amp=True,
                
                # Output
                project='./results',
                name=f"helmet_{config['name'].split()[0].replace('🔥', 'full').replace('⚖️', 'balanced').replace('❄️', 'efficient').replace('🛡️', 'minimal').lower()}",
                exist_ok=True,
                
                # Checkpoints
                save_period=config['save_period'],
                
                # Seed
                seed=42,
                
                # Augmentations (optimized for generalization)
                mosaic=1.0,
                mixup=0.15,
                copy_paste=0.1,
                degrees=10,
                translate=0.1,
                scale=0.5,
                shear=5.0,
                perspective=0.0002,
                flipud=0.0,
                fliplr=0.5,
                hsv_h=0.015,
                hsv_s=0.7,
                hsv_v=0.4,
               #  blur=0.01,
                
                # Optimizer
                optimizer='AdamW',
                lr0=0.001,
                lrf=0.01,
                momentum=0.937,
                weight_decay=0.0005,
                warmup_epochs=3,
                cos_lr=True,
                
                # Loss
                box=7.5,
                cls=0.5,
                dfl=1.5,
                
                # Validation
                val=True,
                plots=True,
                verbose=True,
                
                # Advanced
                close_mosaic=10,
                rect=False,
            )
        
        monitor.monitoring = False
        print("\n\n" + "="*60)
        print("✅ TRAINING COMPLETE!")
        print("="*60)
        
        # Final stats
        temp, util = monitor.get_gpu_stats()
        if temp:
            print(f"\n🌡️ Final GPU: {temp}°C, {util}%")
        
        # Validation
        print("\n🧪 Running validation...")
        metrics = model.val()
        
        print("\n📊 FINAL METRICS:")
        print(f"  mAP50:     {metrics.box.map50:.3f}")
        print(f"  mAP50-95:  {metrics.box.map:.3f}")
        print(f"  Precision: {metrics.box.mp:.3f}")
        print(f"  Recall:    {metrics.box.mr:.3f}")
        print("="*60 + "\n")
        
    except KeyboardInterrupt:
        monitor.monitoring = False
        print("\n\n⚠️ Training interrupted by user")
    except Exception as e:
        monitor.monitoring = False
        print(f"\n\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

def resume_training_with_mode():
    """Resume training with choice of mode"""
    checkpoint, project_name = find_last_checkpoint()
    
    if not checkpoint:
        print("\n❌ No checkpoint found!")
        print("💡 Start new training instead\n")
        return
    
    print("\n🔄 RESUME TRAINING")
    print("="*60)
    print(f"✅ Found checkpoint: {checkpoint}")
    print(f"📁 Project: {project_name}")
    
    # Check checkpoint details
    try:
        ckpt = torch.load(checkpoint, map_location='cpu')
        epoch = ckpt.get('epoch', -1)
        print(f"📊 Last completed epoch: {epoch}")
    except Exception as e:
        print(f"⚠️ Could not read checkpoint: {e}")
    
    print("\n" + "="*60)
    print("Choose training mode to resume with:")
    print("="*60)
    print("1. 🔥 Full Performance (95% GPU, fast)")
    print("2. ⚖️ Balanced (85% GPU, recommended)")
    print("3. ❄️ Efficient (80% GPU, cool)")
    print("4. 🛡️ Minimal (75% GPU, ultra-safe)")
    print("="*60)
    
    choice = input("\nChoice (1-4) [default: 2]: ").strip() or "2"
    mode_map = {'1': 'full', '2': 'balanced', '3': 'efficient', '4': 'minimal'}
    mode = mode_map.get(choice, 'balanced')
    
    # Check system
    ram_available = check_system_health()
    ram_gb = ram_available / 1024**3
    vram_gb = torch.cuda.get_device_properties(0).total_memory / 1024**3 if torch.cuda.is_available() else 4
    
    # Get config
    config = get_training_config(mode, vram_gb, ram_gb)
    
    input("\nPress ENTER to resume training...")
    
    # Train
    train_with_config(config, is_resume=True, checkpoint_path=checkpoint)

def new_training_with_mode():
    """Start new training with mode selection"""
    print("\n🆕 NEW TRAINING")
    print("="*60)
    print("Choose training mode:")
    print("="*60)
    print("1. 🔥 Full Performance (95% GPU)")
    print("   └─ Fast, may heat up (70-75°C)")
    print("   └─ Batch: 12, Workers: 4")
    print("")
    print("2. ⚖️ Balanced (85% GPU) ⭐ RECOMMENDED")
    print("   └─ Good speed, stable (60-68°C)")
    print("   └─ Batch: 10, Workers: 3")
    print("")
    print("3. ❄️ Efficient (80% GPU)")
    print("   └─ Cool & quiet (55-62°C)")
    print("   └─ Batch: 8, Workers: 2")
    print("")
    print("4. 🛡️ Minimal (75% GPU)")
    print("   └─ Ultra-safe (50-58°C)")
    print("   └─ Batch: 4, Workers: 1")
    print("="*60)
    
    choice = input("\nChoice (1-4) [default: 2]: ").strip() or "2"
    mode_map = {'1': 'full', '2': 'balanced', '3': 'efficient', '4': 'minimal'}
    mode = mode_map.get(choice, 'balanced')
    
    # Check system
    ram_available = check_system_health()
    ram_gb = ram_available / 1024**3
    vram_gb = torch.cuda.get_device_properties(0).total_memory / 1024**3 if torch.cuda.is_available() else 4
    
    # Get config
    config = get_training_config(mode, vram_gb, ram_gb)
    
    # Cache option
    if config['cache']:
        print(f"\n💾 Cache enabled: Will load images to RAM ({ram_gb:.1f}GB available)")
        print("   This will make training MUCH faster!")
    else:
        print(f"\n💾 Cache disabled: Will read from disk")
        if ram_gb > 8:
            enable_cache = input("   Enable cache? (y/n) [y]: ").strip().lower() or 'y'
            if enable_cache == 'y':
                config['cache'] = True
    
    input("\nPress ENTER to start training...")
    
    # Train
    train_with_config(config, is_resume=False)

def diagnose_stuck():
    """Diagnose stuck training"""
    print("\n🔍 STUCK TRAINING DIAGNOSTIC")
    print("="*60)
    
    # Check processes
    print("\n1️⃣ Checking Python processes...")
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
        try:
            if 'python' in proc.info['name'].lower():
                cpu = proc.cpu_percent(interval=0.1)
                print(f"  PID {proc.info['pid']}: CPU {cpu}%")
                if cpu < 5:
                    print(f"    ⚠️ Very low CPU - may be stuck")
        except:
            pass
    
    # Check checkpoints
    print("\n2️⃣ Checking training progress...")
    results_dir = Path('./results')
    if results_dir.exists():
        for project in results_dir.iterdir():
            if project.is_dir():
                last_pt = project / 'weights' / 'last.pt'
                if last_pt.exists():
                    mtime = time.time() - last_pt.stat().st_mtime
                    print(f"  {project.name}:")
                    print(f"    Last updated: {mtime/60:.1f} min ago")
                    if mtime > 600:
                        print(f"    ⚠️ No progress for 10+ min")
    
    # Recommendations
    print("\n3️⃣ SOLUTIONS:")
    print("  If stuck:")
    print("  1. Stop training (Ctrl+C)")
    print("  2. Run option 1 (Resume with new mode)")
    print("  3. Try lower mode (Efficient or Minimal)")

def kill_processes():
    """Kill stuck processes"""
    print("\n☠️ KILL STUCK PROCESSES")
    print("="*60)
    
    killed = False
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if 'python' in proc.info['name'].lower():
                cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                if 'yolo' in cmdline.lower() or 'train' in cmdline:
                    print(f"\nFound: PID {proc.info['pid']}")
                    print(f"Command: {cmdline[:80]}...")
                    resp = input("Kill? (y/n): ")
                    if resp.lower() == 'y':
                        proc.kill()
                        print("✅ Killed")
                        killed = True
        except:
            pass
    
    if not killed:
        print("\nNo training processes found")

def quick_test():
    """Quick test on validation set"""
    print("\n🧪 QUICK TEST MODE")
    print("="*60)
    
    weights = Path('./results/helmet_balanced/weights/best.pt')
    if not weights.exists():
        print("❌ No trained model found. Run training first!")
        return
    
    print(f"📥 Loading model: {weights}")
    model = YOLO(str(weights))
    
    print("🔍 Running validation...")
    metrics = model.val(data='./datasets/detect-helmet/data.yaml')
    
    print("\n📊 VALIDATION RESULTS:")
    print(f"  - mAP50: {metrics.box.map50:.3f}")
    print(f"  - mAP50-95: {metrics.box.map:.3f}")
    print(f"  - Precision: {metrics.box.mp:.3f}")
    print(f"  - Recall: {metrics.box.mr:.3f}")
    
    # Per-class metrics
    print("\n📋 PER-CLASS PERFORMANCE:")
   #  class_names = [
   #      "space-empty", "space-occupied", "pothole",
   #      "With Helmet", "Without Helmet", "licence", "Bike", "Car"
   #  ]
    class_names = [
        "with_helmet", "no_helmet", "motorcycle"
    ]
    
    if hasattr(metrics.box, 'ap_class_index'):
        for i, class_name in enumerate(class_names):
            if i < len(metrics.box.ap):
                print(f"  - {class_name}: {metrics.box.ap[i]:.3f}")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🎮 ALL-IN-ONE TRAINING SCRIPT")
    print("="*60)
    print("Features:")
    print("  • Resume from checkpoint")
    print("  • GPU usage limiting (4 modes)")
    print("  • Anti-stuck optimizations")
    print("  • Real-time GPU monitoring")
    print("="*60 + "\n")
    
    print("Choose option:")
    print("1. 🔄 Resume Training (with mode selection)")
    print("2. 🆕 New Training (with mode selection)")
    print("3. 🔍 Diagnose Stuck Training")
    print("4. ☠️ Kill Stuck Processes")
    print("5. 🔍 Quick Test Model")
    print("6. Exit")
    
    choice = input("\nChoice (1-6): ").strip()
    
    if choice == '1':
        resume_training_with_mode()
    elif choice == '2':
        new_training_with_mode()
    elif choice == '3':
        diagnose_stuck()
    elif choice == '4':
        kill_processes()
    elif choice == '5':
        quick_test()
    else:
        print("Exiting...")