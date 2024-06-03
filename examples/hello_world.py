"""
Sample python script using logging to output a Hello World message
"""
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s %(message)s')

my_message = "Hello, World!"

logging.info(my_message)
