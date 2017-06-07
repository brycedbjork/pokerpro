from back import *


# main function
def main():
	start = time.process_time()

	print(analyze([1, 13, 12, 11, 10]))

	elapsed = time.process_time() - start
	print(elapsed)
# run main function
if __name__ == "__main__":
	main()
