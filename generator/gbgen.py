import markdown2
import os

DEFAULT_SOURCE_CONTENT_PATH = 'source_content'


def compile_content(source_path):
	for file in os.listdir(source_path):
		print(file)

def main():
	compile_content(DEFAULT_SOURCE_CONTENT_PATH)

if __name__ == '__main__':
	main()