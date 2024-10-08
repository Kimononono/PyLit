import libcst as cst

class ClassFunctionInserter(cst.CSTTransformer):
    def __init__(self, class_name, function_node):
        self.class_name = class_name
        self.function_node = function_node

    def leave_ClassDef(self, original_node, updated_node):
        if original_node.name.value == self.class_name:
            # Insert the new function into the class body
            return updated_node.with_changes(body=updated_node.body.with_changes(body=updated_node.body.body + (self.function_node,)))
        return updated_node

import libcst as cst

class ClassPropertyInserter(cst.CSTTransformer):
    def __init__(self, class_name, property_node):
        self.class_name = class_name
        self.property_node = property_node

    def leave_ClassDef(self, original_node, updated_node):
        # Check for the __init__ method
        init_method = self.find_init_method(updated_node)

        # Update or create the __init__ method
        if init_method:
            updated_body = self.add_property_to_init(updated_node.body.body)
        else:
            updated_body = self.create_init_method(updated_node.body.body)

        # Return the updated node
        return updated_node.with_changes(
            body=updated_node.body.with_changes(body=updated_body)
        )

    def find_init_method(self, updated_node):
        """Check if __init__ method exists and return it if found."""
        for item in updated_node.body.body:
            if isinstance(item, cst.FunctionDef) and item.name.value == "__init__":
                return item
        return None

    def add_property_to_init(self, class_body):
        """Add property to the existing __init__ method."""
        updated_body = []
        for item in class_body:
            if isinstance(item, cst.FunctionDef) and item.name.value == "__init__":
                # Update the existing __init__ method
                new_body = item.body.with_changes(
                    body=item.body.body + (self.property_node,)
                )
                updated_body.append(item.with_changes(body=new_body))
            else:
                updated_body.append(item)
        return updated_body

    def create_init_method(self, class_body):
        """Create a new __init__ method if it doesn't exist."""
        # Create the __init__ function with the property
        new_init = cst.FunctionDef(
            name=cst.Name("__init__"),
            params=cst.Parameters(params=[cst.Param(name=cst.Name("self"))]),
            body=cst.IndentedBlock(body=[self.property_node])
        )
        # Add the new __init__ method to the class body
        return class_body + (new_init,)

