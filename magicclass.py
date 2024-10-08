import os
import inspect
import subprocess
import inspect
import subprocess
import types
import os
from typing import Any

# from .semanticUtils import classify
from .classinserter import ClassFunctionInserter, ClassPropertyInserter
import libcst as cst
import inspect
import linecache
import marvin

class MagicBaseClass:
    def __init__(self):
        pass    
    def createFunction(self, functionName):
        """
        Simulate an async function that generates a function string
        based on the function name.
        """
        # In a real scenario, this could involve network calls or other logic
        # For now, we are just returning a simple function as a string
        return f"\ndef {functionName}(self):\n    print('Function {functionName} was called')\n"

    def createProperty(self, propertyName):
        return f"\nself.{propertyName} = None" 

    def find_class_file(self):
        """
        Use inspect to find the file where the current class is implemented.
        """
        # Get the source file of the current class (ExtendedExec)
        current_file = inspect.getfile(self.__class__)
        return current_file

    def append_to_file(self, file_path, function_str, _type):
        """
        Append the function string to the end of the given file.
        """
        print("APPENINDING TO FILE TYPE: ", _type)
        class_name = self.__class__.__name__
        with open(file_path, 'r') as f:
            module_tree = cst.parse_module(f.read())

        # Parse the new function into a CST node
        node = cst.parse_statement(function_str)
        
        # Apply the transformation to insert the function
        if _type == "Function":
            transformer = ClassFunctionInserter(class_name, node)
        elif _type == "Property":
            transformer = ClassPropertyInserter(class_name, node)
        else:
            raise Exception("What the fuck it isnt a Function or a Property inside append_to_file")

        new_tree = module_tree.visit(transformer)

        with open(file_path, 'w') as f:
            f.write(new_tree.code)

    def git_commit(self, file_path, function_name):
        """
        Perform a git commit for the modified file. If the file is not in a Git repository, raise an error.
        """
        # Get the directory where the file is located
        file_dir = os.path.dirname(os.path.abspath(file_path))

        # Check if the directory is inside a Git repository
        try:
            result = subprocess.run(['git', 'rev-parse', '--is-inside-work-tree'],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, cwd=file_dir)
            if result.stdout.decode().strip() != 'true':
                raise EnvironmentError(f"Directory {file_dir} is not inside a Git repository.")

        except subprocess.CalledProcessError:
            raise EnvironmentError(f"Directory {file_dir} is not inside a Git repository.")

        # Add the file to the staging area
        subprocess.run(['git', 'add', file_path], check=True, cwd=file_dir)

        # Commit the change with a message
        subprocess.run(['git', 'commit', '-m', f"Added function {function_name} to {file_path}"], check=True, cwd=file_dir)

        print(f"Successfully committed {function_name} to {file_path}.")


    def exec_function(self, node_name, _type):
        """
        Extended exec function that generates, appends, and commits
        a dynamically created function.
        """
        # Step 1: Generate the function body (string)
        function_str = self.createFunction(node_name)
        property_str = self.createProperty(node_name)
        if _type == "Function":
            chosen = function_str
        elif _type == "Property":
            chosen = property_str
        
        # Step 2: Find the file where this class is implemented
        class_file = self.find_class_file()
        
        # Step 3: Append the new function to the file
        self.append_to_file(class_file, chosen, _type)

        # Step 4: Execute the newly generated function in the current context
        context = {}
        exec(function_str, context)
        assignment = None
        print("EXECUTING: ")
        print(function_str)
        print('------')
        if _type == "Function":
            assignment = types.MethodType(context[node_name], self)
        elif _type == "Property":
            assignment = context.get(node_name, None)

        setattr(self, node_name, assignment)

        # Step 5: Git commit the change
        # self.git_commit(class_file, node_name)


    def __getattr__(self, name):
        """
        Override __getattr__ to dynamically create a function if it does not exist.
        """
        # if hasattr(self.executor, name):
        #     return getattr(self.executor,name)

        stack = inspect.stack()
        
        # The caller's frame is typically at position 1
        caller_frame = stack[1]
        
        # Extract information from the frame
        file_name = caller_frame.filename
        line_number = caller_frame.lineno
        
        # Fetch the actual line of code that triggered __getattribute__
        line = linecache.getline(file_name, line_number).strip()

        # guessed_type = classify(line + ", specifically " + name, ["Function", "Property"]) 
        guessed_type = marvin.classify(
                line + ", specifically " + name,
                labels=["Function", "Property"]
                )
        
        print(f"__getattr__ SHORT was called by: {line} (line {line_number} in {file_name})")
        
        #print("has attr: ", name, " is : ", hasattr(self,name))
        print(f"Method '{name}' does not exist. Creating it dynamically...")

        # Dynamically create the method using ExtendedExec
        if guessed_type == "Function":
            print("ADDING FUNCTION")
            self.exec_function(name, guessed_type)
        elif guessed_type == "Property":
            print("ADDING PROPERTY")
            self.exec_function(name, guessed_type)
        
        return getattr(self, name)


