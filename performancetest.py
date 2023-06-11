import requests
import time

def measure_ttfb(url, num=1):
    ttfb_total = 0
    for _ in range(num):
        start_time = time.time()
        response = requests.get(url)
        ttfb_total += time.time() - start_time
    return ttfb_total / num

# Test the function
url = 'https://silkresource.com/store'  # replace with your URL
num_tests = 5  # replace with your desired number of tests
average_ttfb = measure_ttfb(url, num_tests)
print(f"The average TTFB for {url} over {num_tests} tests is {average_ttfb} seconds.")
