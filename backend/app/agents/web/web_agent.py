import os
import time
import threading
from urllib.parse import urlparse, urljoin
from playwright.sync_api import sync_playwright

class WebTestingAgent:
    def __init__(self, headless=True):
        self.headless = headless
        self.screenshot_dir = 'screenshots'
        if not os.path.exists(self.screenshot_dir):
            os.makedirs(self.screenshot_dir)

    def run_test(self, start_url, max_pages=5):
        """
        Crawls the website starting from start_url, visiting up to max_pages.
        Returns detailed results for each page visited.
        """
        results = {
            'status': 'completed',
            'start_url': start_url,
            'pages': [], # List of {url, title, screenshot, issues, duration}
            'summary': {'total_pages': 0, 'total_issues': 0},
            'duration': 0
        }
        
        overall_start_time = time.time()
        visited_urls = set()
        queue = [start_url]
        
        # Extract domain to keep crawl within site
        start_domain = urlparse(start_url).netloc

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=self.headless)
                context = browser.new_context(viewport={'width': 1280, 'height': 720})
                
                while queue and len(visited_urls) < max_pages:
                    current_url = queue.pop(0)
                    if current_url in visited_urls:
                        continue
                        
                    visited_urls.add(current_url)
                    
                    page_result = {
                        'url': current_url,
                        'issues': [],
                        'screenshot': None,
                        'title': '',
                        'links_found': 0
                    }
                    
                    page_start_time = time.time()
                    page = context.new_page()

                    # -- Setup Listeners for this page --
                    page.on("console", lambda msg: page_result['issues'].append({
                        'type': 'console', 
                        'level': msg.type, 
                        'text': msg.text
                    }) if msg.type in ['error', 'warning'] else None)
                    
                    page.on("requestfailed", lambda req: page_result['issues'].append({
                        'type': 'network_error', 
                        'url': req.url, 
                        'error': req.failure
                    }))
                    
                    page.on("response", lambda resp: page_result['issues'].append({
                        'type': 'http_error', 
                        'url': resp.url, 
                        'status': resp.status
                    }) if resp.status >= 400 else None)

                    try:
                        print(f"Crawling: {current_url}")
                        response = page.goto(current_url, wait_until="domcontentloaded", timeout=20000)
                        
                        # Wait a bit for dynamic content
                        page.wait_for_timeout(2000)
                        
                        page_result['title'] = page.title()

                        # Screenshot
                        timestamp = int(time.time())
                        safe_name = urlparse(current_url).path.replace('/', '_').strip('_')
                        if not safe_name: safe_name = "home"
                        filename = f"web_{timestamp}_{safe_name}.png"
                        filepath = os.path.join(self.screenshot_dir, filename)
                        
                        page.screenshot(path=filepath)
                        page_result['screenshot'] = filename

                        # Extract internal links for crawling
                        links = page.locator("a").all()
                        page_result['links_found'] = len(links)
                        
                        for link in links:
                            try:
                                href = link.get_attribute("href")
                                if href:
                                    full_url = urljoin(current_url, href)
                                    parsed = urlparse(full_url)
                                    # Only follow internal links
                                    if parsed.netloc == start_domain and full_url not in visited_urls:
                                        # Simple heuristic to avoid junk types
                                        if not any(ext in parsed.path.lower() for ext in ['.png', '.jpg', '.pdf', '.css', '.js']):
                                            queue.append(full_url)
                            except:
                                continue

                    except Exception as e:
                        page_result['issues'].append({'type': 'crawl_error', 'message': str(e)})
                    
                    page_result['duration'] = time.time() - page_start_time
                    results['pages'].append(page_result)
                    page.close()
                
                browser.close()

        except Exception as e:
            results['status'] = 'failed'
            results['error'] = str(e)
            print(f"Crawl failed: {e}")

        results['duration'] = time.time() - overall_start_time
        results['summary']['total_pages'] = len(results['pages'])
        results['summary']['total_issues'] = sum(len(p['issues']) for p in results['pages'])
        
        return results
