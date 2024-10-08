import asyncio
# magicClass.py

# GOOD IDEA
# A auto formatter for print statements to make them look at pretty and neat

async def main():
    from .test.library import Library
    library_instance = Library()

    # Calling an existing method
    library_instance.existing_method()

    # Call a method that doesn't exist, which will trigger dynamic creation
    library_instance.new_method()
    #print(library_instance.books)
    library_instance.books = 5

if __name__ == "__main__":

    with open('/home/hunte/programming/messaround/smartdb/test/original_library.py','r') as f:
        original_contents = f.read()
    print("Overwriting library.py with:")
    print(original_contents)
    print("\n--------\n\n")
    with open('/home/hunte/programming/messaround/smartdb/test/library.py','w') as f:
        f.write(original_contents)
    asyncio.run(main())

