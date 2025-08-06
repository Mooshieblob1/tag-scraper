#!/usr/bin/env python3
"""
Rate Limit Monitor for Danbooru Artist Scraper
Tests and monitors the enhanced 429 detection system
"""

import time
import json
from datetime import datetime, timedelta
from scraper import DanbooruArtistScraper
from typing import Dict, List
import logging

# Setup logging for monitoring
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rate_limit_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RateLimitMonitor:
    def __init__(self):
        self.scraper = DanbooruArtistScraper()
        self.test_results = []
        self.monitoring_data = []
    
    def test_429_detection(self):
        """Test the 429 detection system with controlled requests"""
        logger.info("🧪 Starting 429 detection test...")
        
        # Test 1: Normal rate limiting
        logger.info("📊 Test 1: Normal rate limiting behavior")
        start_time = time.time()
        
        for i in range(5):
            page_id = f"a{i}"
            logger.info(f"   Testing page {page_id}")
            
            result = self.scraper.get_page(page_id)
            status = self.scraper.get_rate_limit_status()
            
            self.test_results.append({
                'test': 'normal_rate_limiting',
                'page': page_id,
                'timestamp': datetime.now(),
                'status': status,
                'result_count': len(result) if result else 0,
                'response_time': time.time() - start_time
            })
            
            logger.info(f"   Status: {status['health_status']} - {status['current_rate_limit']}")
            
            if status['total_429s'] > 0:
                logger.warning(f"   ⚠️  Got 429 error: {status['total_429s']} total, {status['consecutive_429s']} consecutive")
            
            time.sleep(1)  # Small delay between tests
        
        logger.info("✅ Test 1 completed")
    
    def test_aggressive_rate_limiting(self):
        """Test aggressive requesting to trigger 429 responses"""
        logger.info("🔥 Test 2: Aggressive rate limiting (may trigger 429s)")
        
        # Temporarily reduce rate limiting to trigger 429s
        original_interval = self.scraper.min_request_interval
        self.scraper.min_request_interval = 0.05  # 20 req/sec - likely to trigger 429s
        
        try:
            for i in range(10):
                page_id = f"a{i}"
                logger.info(f"   Aggressive test page {page_id}")
                
                start_time = time.time()
                result = self.scraper.get_page(page_id)
                end_time = time.time()
                
                status = self.scraper.get_rate_limit_status()
                
                self.test_results.append({
                    'test': 'aggressive_rate_limiting',
                    'page': page_id,
                    'timestamp': datetime.now(),
                    'status': status,
                    'result_count': len(result) if result else 0,
                    'response_time': end_time - start_time
                })
                
                logger.info(f"   Response time: {end_time - start_time:.2f}s")
                logger.info(f"   Status: {status['health_status']} - {status['current_rate_limit']}")
                
                if status['total_429s'] > 0:
                    logger.warning(f"   🚫 429 detected: {status['total_429s']} total, {status['consecutive_429s']} consecutive")
                    logger.info(f"   🔄 Adaptive cooldown: {status['adaptive_cooldown_remaining']:.1f}s remaining")
                
                # Stop if we hit too many 429s
                if status['consecutive_429s'] >= 3:
                    logger.warning("   🛑 Stopping aggressive test due to multiple 429s")
                    break
        
        finally:
            # Restore original rate limiting
            self.scraper.min_request_interval = original_interval
            logger.info(f"   🔄 Restored original rate limiting: {1/original_interval:.1f} req/sec")
        
        logger.info("✅ Test 2 completed")
    
    def monitor_recovery(self, duration_minutes: int = 5):
        """Monitor rate limiting recovery over time"""
        logger.info(f"📈 Test 3: Monitor recovery over {duration_minutes} minutes")
        
        end_time = datetime.now() + timedelta(minutes=duration_minutes)
        
        while datetime.now() < end_time:
            status = self.scraper.get_rate_limit_status()
            
            self.monitoring_data.append({
                'timestamp': datetime.now(),
                'status': status
            })
            
            logger.info(f"   Recovery status: {status['health_status']} - {status['current_rate_limit']}")
            
            if status['consecutive_successes'] > 0:
                logger.info(f"   ✅ Consecutive successes: {status['consecutive_successes']}")
            
            if status['adaptive_cooldown_remaining'] > 0:
                logger.info(f"   ⏸️  Cooldown remaining: {status['adaptive_cooldown_remaining']:.1f}s")
            
            time.sleep(30)  # Check every 30 seconds
        
        logger.info("✅ Test 3 completed")
    
    def generate_report(self):
        """Generate a comprehensive report of the 429 detection system"""
        logger.info("📋 Generating comprehensive report...")
        
        # Calculate statistics
        total_tests = len(self.test_results)
        tests_with_429s = len([t for t in self.test_results if t['status']['total_429s'] > 0])
        max_consecutive_429s = max([t['status']['consecutive_429s'] for t in self.test_results], default=0)
        
        final_status = self.scraper.get_rate_limit_status()
        
        report = {
            'test_summary': {
                'total_tests': total_tests,
                'tests_with_429s': tests_with_429s,
                'max_consecutive_429s': max_consecutive_429s,
                'test_success_rate': ((total_tests - tests_with_429s) / total_tests * 100) if total_tests > 0 else 0
            },
            'final_status': final_status,
            'test_results': self.test_results,
            'monitoring_data': self.monitoring_data,
            'generated_at': datetime.now().isoformat()
        }
        
        # Save report to file
        with open('rate_limit_test_report.json', 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        # Print summary
        print("\n" + "="*60)
        print("🏁 RATE LIMIT TEST REPORT")
        print("="*60)
        print(f"📊 Total tests run: {total_tests}")
        print(f"🚫 Tests with 429s: {tests_with_429s}")
        print(f"📈 Test success rate: {report['test_summary']['test_success_rate']:.1f}%")
        print(f"🔄 Max consecutive 429s: {max_consecutive_429s}")
        print(f"🏥 Final health status: {final_status['health_status']}")
        print(f"⚡ Final rate limit: {final_status['current_rate_limit']}")
        print(f"📁 Detailed report saved to: rate_limit_test_report.json")
        print("="*60)
        
        return report
    
    def run_full_test_suite(self):
        """Run the complete test suite"""
        logger.info("🚀 Starting full 429 detection test suite...")
        
        try:
            # Test normal behavior
            self.test_429_detection()
            
            # Test aggressive behavior to trigger 429s
            self.test_aggressive_rate_limiting()
            
            # Monitor recovery
            self.monitor_recovery(duration_minutes=2)  # Shorter for testing
            
            # Generate final report
            report = self.generate_report()
            
            logger.info("🎉 Full test suite completed successfully!")
            return report
            
        except Exception as e:
            logger.error(f"❌ Test suite failed: {e}")
            raise

def main():
    """Main function to run the rate limit monitor"""
    print("🎯 Danbooru Rate Limit Monitor")
    print("=" * 40)
    
    monitor = RateLimitMonitor()
    
    print("Choose test mode:")
    print("1. Quick test (normal rate limiting only)")
    print("2. Aggressive test (may trigger 429s)")
    print("3. Full test suite (recommended)")
    print("4. Monitor current status only")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == "1":
        print("\n🧪 Running quick test...")
        monitor.test_429_detection()
        monitor.generate_report()
        
    elif choice == "2":
        print("\n🔥 Running aggressive test (may get 429 errors)...")
        confirm = input("This may trigger rate limiting. Continue? (y/N): ").strip().lower()
        if confirm == 'y':
            monitor.test_aggressive_rate_limiting()
            monitor.generate_report()
        else:
            print("❌ Cancelled")
            
    elif choice == "3":
        print("\n🚀 Running full test suite...")
        confirm = input("This will run comprehensive tests. Continue? (y/N): ").strip().lower()
        if confirm == 'y':
            monitor.run_full_test_suite()
        else:
            print("❌ Cancelled")
            
    elif choice == "4":
        print("\n📊 Current rate limiting status:")
        status = monitor.scraper.get_rate_limit_status()
        print(json.dumps(status, indent=2, default=str))
        
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()
