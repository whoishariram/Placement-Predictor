"""
Placement Predictor - Monitoring & Health Check Module
Health checks, application status, model status, database status, system metrics
"""

import os
import time
import platform
import json
from datetime import datetime
from functools import wraps


class HealthChecker:
    """
    Health and status checker for the Placement Predictor application

    Provides:
    - Health check API responses
    - Application status information
    - Model status
    - Database status
    - System resource usage
    """

    def __init__(self, config=None):
        """Initialize health checker"""
        self.config = config
        self.start_time = time.time()
        self._health_cache = {}
        self._last_cache_update = 0

    def get_uptime(self):
        """Get application uptime in seconds"""
        return time.time() - self.start_time

    def get_uptime_formatted(self):
        """Get formatted uptime string"""
        uptime = self.get_uptime()
        days = int(uptime // 86400)
        hours = int((uptime % 86400) // 3600)
        minutes = int((uptime % 3600) // 60)
        seconds = int(uptime % 60)

        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        parts.append(f"{seconds}s")
        return ' '.join(parts)

    def check_model_status(self):
        """Check if ML model is available"""
        model_path = None
        if self.config:
            model_path = getattr(self.config, 'MODEL_PATH', None) or \
                         os.path.join(getattr(self.config, 'MODEL_DIR', ''), 'best_model.pkl')

        if model_path and os.path.exists(model_path):
            model_size = os.path.getsize(model_path)
            model_mtime = datetime.fromtimestamp(os.path.getmtime(model_path))
            return {
                'status': 'available',
                'path': model_path,
                'size_bytes': model_size,
                'size_mb': round(model_size / (1024 * 1024), 2),
                'last_modified': model_mtime.isoformat()
            }

        return {
            'status': 'not_found',
            'message': 'No trained model found. Train the model first.'
        }

    def check_database_status(self, db=None):
        """Check database connectivity"""
        if db is None:
            return {
                'status': 'not_configured',
                'message': 'Database session not available'
            }

        try:
            # Try a simple query
            db.session.execute(db.text('SELECT 1'))
            return {
                'status': 'connected',
                'message': 'Database is operational'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Database error: {str(e)}'
            }

    def check_disk_usage(self):
        """Check disk usage for important directories"""
        dirs_to_check = ['dataset', 'model', 'uploads', 'logs', 'reports']
        disk_info = {}

        for dir_name in dirs_to_check:
            dir_path = None
            if self.config:
                config_dir = getattr(self.config, f'{dir_name.upper()}_DIR', None)
                if config_dir:
                    dir_path = config_dir
                else:
                    base = getattr(self.config, 'BASE_DIR', os.getcwd())
                    dir_path = os.path.join(base, dir_name)
            else:
                dir_path = os.path.join(os.getcwd(), dir_name)

            if os.path.exists(dir_path):
                total_size = 0
                file_count = 0
                for dirpath, dirnames, filenames in os.walk(dir_path):
                    for f in filenames:
                        fp = os.path.join(dirpath, f)
                        try:
                            total_size += os.path.getsize(fp)
                            file_count += 1
                        except OSError:
                            pass

                disk_info[dir_name] = {
                    'path': dir_path,
                    'exists': True,
                    'file_count': file_count,
                    'size_bytes': total_size,
                    'size_mb': round(total_size / (1024 * 1024), 2)
                }
            else:
                disk_info[dir_name] = {
                    'path': dir_path,
                    'exists': False,
                    'file_count': 0,
                    'size_bytes': 0,
                    'size_mb': 0
                }

        return disk_info

    def get_system_info(self):
        """Get system information"""
        return {
            'platform': platform.platform(),
            'python_version': platform.python_version(),
            'hostname': platform.node(),
            'architecture': platform.machine()
        }

    def get_overall_status(self):
        """Get complete application status"""
        model_status = self.check_model_status()

        status = {
            'application': {
                'name': 'Placement Predictor',
                'version': '1.0.0',
                'status': 'running',
                'uptime': self.get_uptime_formatted(),
                'uptime_seconds': self.get_uptime(),
                'started_at': datetime.fromtimestamp(
                    self.start_time
                ).isoformat(),
                'current_time': datetime.utcnow().isoformat()
            },
            'system': self.get_system_info(),
            'model': model_status,
            'disk_usage': self.check_disk_usage()
        }

        return status

    def quick_health(self):
        """Quick health check (lightweight)"""
        model_exists = False
        if self.config:
            model_path = getattr(self.config, 'MODEL_PATH', None)
            if model_path:
                model_exists = os.path.exists(model_path)

        return {
            'status': 'healthy',
            'uptime': self.get_uptime_formatted(),
            'model_loaded': model_exists,
            'timestamp': datetime.utcnow().isoformat()
        }


class Monitor:
    """
    Performance monitoring decorators and utilities

    Measures execution time for critical operations
    """

    @staticmethod
    def timed(operation_name=None):
        """
        Decorator to measure execution time of functions

        Usage:
            @Monitor.timed('data_cleaning')
            def clean_dataset():
                ...
        """
        def decorator(f):
            @wraps(f)
            def decorated(*args, **kwargs):
                start = time.time()
                result = f(*args, **kwargs)
                elapsed = time.time() - start
                name = operation_name or f.__name__
                print(f"⏱️  {name}: {elapsed:.4f}s")
                return result
            return decorated
        return decorator

    @staticmethod
    def benchmark(dataset_sizes=None, iterations=3):
        """
        Decorator to benchmark functions at different dataset sizes

        Usage:
            @Monitor.benchmark(dataset_sizes=[100, 500, 1000])
            def process_data(df):
                ...
        """
        if dataset_sizes is None:
            dataset_sizes = [100, 500, 1000]

        def decorator(f):
            @wraps(f)
            def decorated(*args, **kwargs):
                results = []
                for size in dataset_sizes:
                    times = []
                    for i in range(iterations):
                        start = time.time()
                        result = f(*args, **kwargs)
                        elapsed = time.time() - start
                        times.append(elapsed)
                    avg_time = sum(times) / len(times)
                    results.append({
                        'size': size,
                        'avg_time': round(avg_time, 4),
                        'min_time': round(min(times), 4),
                        'max_time': round(max(times), 4),
                        'iterations': iterations
                    })
                    print(f"  📊 {f.__name__} ({size} records): {avg_time:.4f}s avg")

                return result
            return decorated
        return decorator

    @staticmethod
    def print_report(results):
        """Print benchmark timing report"""
        print("\n" + "=" * 60)
        print("📊 PERFORMANCE BENCHMARK REPORT")
        print("=" * 60)
        print(f"{'Operation':<30} {'Size':<10} {'Avg Time':<12} {'Min':<12} {'Max':<12}")
        print("-" * 60)
        for r in results:
            print(f"{r['operation']:<30} {r['size']:<10} "
                  f"{r['avg_time']:<12.4f} {r['min_time']:<12.4f} {r['max_time']:<12.4f}")
        print("=" * 60)
