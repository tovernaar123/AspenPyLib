import win32com.client

# Connect to Aspen Plus
aspen = win32com.client.Dispatch("Apwn.Document")
aspen.InitFromFile(r"C:\Programming\delft\Aspen\sim1.apw")
aspen.Visible = True

blocks_node = aspen.Application.Tree.FindNode(r"\Data")
print(blocks_node)

# blocks_node = aspen.Application.Tree
# print(dir(blocks_node))
# print(blocks_node.GetTypeInfoCount())
# print(help(blocks_node.GetTypeInfo))
# print(help(blocks_node.BrowseNext))
# print(help(blocks_node.Export))
# res = blocks_node.Export(r"C:\Programming\delft\Aspen\results")
# print(res)
# print(blocks_node.Elements)

print(blocks_node.Blocks.Elements.Count)
# Loop through all blocks
for i in range(blocks_node.Blocks.Elements.Count):
    block = blocks_node.Blocks.Elements.Item(i)
    print(f"Block name: {block.Output.WNET.value}")

