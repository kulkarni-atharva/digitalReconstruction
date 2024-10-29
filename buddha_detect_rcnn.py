import torch
import torchvision
from torchvision.models.detection import FasterRCNN
import torchvision.transforms as transforms
from torchvision.models.detection.rpn import AnchorGenerator
from torch.utils.data import DataLoader, Dataset
from PIL import Image
import os
import xml.etree.ElementTree as ET
import re
import matplotlib.pyplot as plt
import matplotlib.patches as patches

label_map = {"broken" : 1,
             "buddha" : 2}
             #background : 0
                
#extracting bounding box annotations from 
annotation_dir= "./buddha-annotations-coco/" #CHANGE PATH # _/
dir_contents = os.listdir(annotation_dir)
anno_data = [annotation_dir + anno for anno in dir_contents]

#sorting the images
def extract_number(xml_path):
    return int(re.search(r'\d+', xml_path.split("/")[-1]).group())
sorted_xml_paths = sorted(anno_data, key=extract_number)

root = "./test_images/" #CHANGE PATH # _/
dataset_dir = os.listdir(root)
dataset_paths = [root + img for img in dataset_dir]
sorted_dataset_paths = sorted(dataset_paths, key=extract_number)

img_sizes = []
img_data = []
for img_path in sorted_dataset_paths:
    img = Image.open(img_path).convert("RGB")
    # img = transforms.Resize((resized_img_size, resized_img_size))(img)
    img = transforms.ToTensor()(img)
    img_sizes.append(img.shape[1:])
    img_data.append(img)


boxes = []
labels = []
for i, annotation in enumerate(sorted_xml_paths):
    tree = ET.parse(annotation) #parses and creates an element tree object for easy navigation
    root = tree.getroot() #gets root element of the eTree, i.e, the start of xml file
    all_box = []
    all_label = []
    height = img_sizes[i][0]
    width = img_sizes[i][1]
    for obj in root.findall("object"):
            bbox = obj.find("bndbox")
            xmin = int(bbox.find("xmin").text)
            ymin = int(bbox.find("ymin").text)
            xmax = int(bbox.find("xmax").text)
            ymax = int(bbox.find("ymax").text)
            all_box.append([xmin, ymin, xmax, ymax])
            label = obj.find("name").text
            all_label.append(label_map[label])
    boxes.append(torch.as_tensor(all_box))
    labels.append(torch.as_tensor(all_label))

target = []
for i in range(len(boxes)):
    target.append({"boxes": boxes[i], "labels": labels[i]})
dataset = []
for i in range(len(img_data)):
    dataset.append([img_data[i], target[i]])
    

def collate_fn(batch):
    return tuple(zip(*batch))
    
batchSize = 1; #CHANGE BATCH SIZE #

data_loader = DataLoader(
    dataset,
    batch_size=batchSize,
    shuffle=True,
    collate_fn=collate_fn #merges a list of samples to form a mini-batch of Tensor(s)
)

if torch.cuda.is_available():
    device = torch.device("cuda")
else:
    torch.device("cpu")
    
backbone = torchvision.models.resnet50(weights=torchvision.models.ResNet50_Weights.DEFAULT)
backbone = torch.nn.Sequential(*list(backbone.children())[:-2])
backbone.out_channels = 2048 #output feature extractors = 2048

anchor_generator = AnchorGenerator(
    sizes=((16, 32, 64, 128),),
    aspect_ratios=((0.5, 1.0, 2.0),)
)

roi_pooler = torchvision.ops.MultiScaleRoIAlign(
    featmap_names=["0"],  # Feature map names (from the backbone)
    output_size=21,  # RoI pool size
    sampling_ratio=2  # Sampling ratio
)

model = FasterRCNN(
    backbone,
    num_classes=3,  # 1 for buddha, 2 for broken, 0 for background
    rpn_anchor_generator=anchor_generator,
    box_roi_pool=roi_pooler
)

params = [p for p in model.parameters() if p.requires_grad]
optimizer = torch.optim.Adam(params, lr=0.025, weight_decay=0.0005)
lr_scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=3, gamma=0.1)
print("Done")


# Training loop
model.train()
num_epochs = 15
loss_per_epoch = []
for epoch in range(num_epochs):
    print("epochStart")
    total_loss = 0
    for images, targets in data_loader:
        print("-", end="")
        images = list(image for image in images)
        targets = [{k: v for k, v in t.items()} for t in targets]

        optimizer.zero_grad()  # Zero gradients
        loss_dict = model(images, targets)  # Forward pass through the model
        losses = sum(loss for loss in loss_dict.values())  # Sum all losses

        losses.backward()  # Backpropagation
        optimizer.step()  # Optimize weights

        total_loss += losses.item()  # Accumulate loss for the current epoch
        print("|", end="")
    lr_scheduler.step()  # Step the learning rate scheduler
    print(f"\nEpoch [{epoch + 1}/{num_epochs}], Loss: {total_loss:.4f}\n")
    loss_per_epoch.append(.4f)

torch.save(model.state_dict(), "faster_rcnn_buddha_model_v5.pth")

del backbone
del model
backbone = torchvision.models.resnet50(weights=torchvision.models.ResNet50_Weights.DEFAULT)
backbone = torch.nn.Sequential(*list(backbone.children())[:-2])
backbone.out_channels = 2048

anchor_generator = torchvision.models.detection.rpn.AnchorGenerator(
    sizes=((16, 32, 64, 128),),
    aspect_ratios=((0.5, 1.0, 2.0),)
)

roi_pooler = torchvision.ops.MultiScaleRoIAlign(
    featmap_names=["0"],
    output_size=21,
    sampling_ratio=2
)

model = torchvision.models.detection.FasterRCNN(
    backbone,
    num_classes=3,  # Including background
    rpn_anchor_generator=anchor_generator,
    box_roi_pool=roi_pooler
)


model_path = './faster_rcnn_buddha_model_v4.pth'
# Load the trained weights
model.load_state_dict(torch.load(model_path))
model.to(device)
model.eval()



import torchvision.transforms as T
# Define image preprocessing function
transform = T.Compose([
    T.ToTensor()
])

# Load and preprocess the image
# image_path = "path_to_your_custom_image.jpg"
img_dir = './test_images/' #CHANGE PATH # _/
test_images = os.listdir(img_dir)
x = 1
os.makedirs("outputs")
for img in test_images:
	image = Image.open(img).convert("RGB")
	image_tensor = transform(image).to(device)  # Convert to tensor and move to GPU/CPU


	# Pass the image through the model
	with torch.no_grad():
		predictions = model([image_tensor])  # List of predictions

	# Extract the boxes, labels, and scores
	pred_boxes = predictions[0]['boxes'].cpu().numpy()  # Convert to numpy
	pred_labels = predictions[0]['labels'].cpu().numpy()  # Convert to numpy
	pred_scores = predictions[0]['scores'].cpu().numpy()  # Confidence scores

	#save all the pred_boxes and pred_scores somewhere for reviewing later
	threshold = 0.1
	filtered_boxes = pred_boxes[pred_scores >= threshold]
	filtered_labels = pred_labels[pred_scores >= threshold]
	filtered_scores = pred_scores[pred_scores >= threshold]
	# Create a figure and axis
	fig, ax = plt.subplots(1)
	ax.imshow(image)

	# Draw the bounding boxes
	for i, box in enumerate(filtered_boxes):
		xmin, ymin, xmax, ymax = box
		rect = patches.Rectangle((xmin, ymin), xmax - xmin, ymax - ymin, linewidth=2, edgecolor='r', facecolor='none')
		ax.add_patch(rect)
		ax.text(xmin, ymin, f'{filtered_labels[i]}: {filtered_scores[i]:.2f}', color='white', fontsize=5, backgroundcolor='red')

	# Save the image with bounding boxes
	output_image_path = f"outputs/output_test_buddha{x}.jpg" #CHANGE PATH #
	x+=1
	plt.axis('off')  # Turn off axis
	plt.savefig(output_image_path, bbox_inches='tight', pad_inches=0)
	plt.close()  # Close the figure
	print(f"Image saved to {output_image_path}")
