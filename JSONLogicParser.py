

class JSONLogicParser:

    def __init__(self) -> None:
        pass

    def is_operator(self, variable):
        if type(variable) is not str:
            return False # operator must be string value
        
        operators = ['<', '>', '<=', '>=', '=', '!=', '/', 'and', 'or']

        if (variable in operators):
            return True
        
        return False

    def parseLeafNode(self, leafNode):
        result = ''
        operand = ''

        first_key = list(leafNode.keys())[0]

        if first_key == 'var': # if it's a ending leaf / operand
            operand = leafNode['property']
            result = leafNode['var'] + '.' 
        
        if first_key == 'val':
            operand = leafNode['val']
        
        return result + str(operand)

    def inorderTraversal(self, root):
        result = []

        current_node = list(root.keys())[0]
        child_nodes = list(root.values())

        # if current node is NOT an operator then root was an edge leaf/node
        # therefore, do processing for edge leaf
        if not self.is_operator(current_node):  
            return self.parseLeafNode(root)
        
        result = self.inorderTraversal(child_nodes[0][0])
        result = str(result) + ' ' + str(current_node) + ' '
        result = result + self.inorderTraversal(child_nodes[0][1])
        print(result)
        return result
    
    def convertJSONExpressionTreeToString(self, jsonExpressionTree):
        # TODO: case when unexpected format/structture?
        return self.inorderTraversal(jsonExpressionTree)
