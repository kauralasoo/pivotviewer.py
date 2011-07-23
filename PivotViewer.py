import xml.etree.ElementTree as ET
import csv
import os
import deepzoom

class PivotViewerCollection(object):
    """
    Class that defines a PivotViewer collection.
    """
    
    def __init__(self, name, facets = [], items = [], imgBase = "deepzoom/collection.xml"):
        self.name = name
        self.facets = facets
        self.items = items
        self.imgBase = imgBase
    
    def appendFacet(self, facet):
        self.facets.append(facet)
    
    def appendItem(self, item):
        """
        Append item to the collection only if the number of values is 
        equal to the number of facets.
        """
        if len(self.facets) == len(item.values):
            self.items.append(item)
        else:
            raise ValueError("Number of values must be equal to the number of facets.")
    
    def to_cxml(self):
        """
        Convert the collection to CXML representation.
        """
        
        #Define Collection
        xml = ET.Element('Collection')
        xml.set('xmlns:xsi', "http://www.w3.org/2001/XMLSchema-instance")
        xml.set('xmlns:xsd', "http://www.w3.org/2001/XMLSchema")
        xml.set('xmlns:p', "http://schemas.microsoft.com/livelabs/pivot/collection/2009")
        xml.set('Name', self.name)
        xml.set('SchemaVersion',"1.0")
        xml.set('xmlns',"http://schemas.microsoft.com/collection/metadata/2009")
        
        #Add facets
        facetCategories = ET.SubElement(xml, 'FacetCategories')
        for facet in self.facets:
            facetCategoryNode = ET.SubElement(facetCategories, "FacetCategory")
            facetCategoryNode.set("Name", facet.name)
            facetCategoryNode.set("Type", facet.type)
            facetCategoryNode.set("p:IsFilterVisible", str(facet.isFilterVisible).lower())
            facetCategoryNode.set("p:IsMetaDataVisible", str(facet.isMetaDataVisible).lower())
            facetCategoryNode.set("p:IsWordWheelVisible", str(facet.isWordWheelVisible).lower())
        
        #Add items
        itemsNode = ET.SubElement(xml, 'Items')
        itemsNode.set("ImgBase", self.imgBase)
        for item in self.items:
            itemNode = ET.SubElement(itemsNode, 'Item')
            itemNode.set("Name", item.name)
            itemNode.set("Id", item.id)
            itemNode.set("Img", item.imageNumber)
            if item.href:
                itemNode.set("Href", item.href)
            descriptionNode = ET.SubElement(itemNode,'Description')
            descriptionNode.text = item.description
            facetsNode = ET.SubElement(itemNode,'Facets')
            for facet, value in zip(self.facets, item.values):
                facetNode = ET.SubElement(facetsNode, "Facet")
                facetNode.set("Name", facet.name)
                valueNode = ET.SubElement(facetNode, facet.type)
                valueNode.set("Value", str(value))        
      
        indent(xml)
        #ET.dump(xml)
        #tree = ET.ElementTree(xml)
        return ET.tostring(xml)
        #tree.write(path)
    
    def save(self, path):
        """
        Save the collection to a .cxml file.
        """
        cxml = self.to_cxml()
        file = open(path,'w')
        file.write(cxml)
        

class PivotViewerFacet(object):
    """
    Class to store PivotViewer facets
    """
    def __init__(self, name, type, isFilterVisible = True, 
                 isMetaDataVisible = True, isWordWheelVisible = True):
        self.name = name
        self.type = type
        self.isFilterVisible = isFilterVisible
        self.isMetaDataVisible = isMetaDataVisible
        self.isWordWheelVisible = isWordWheelVisible
    
    def __str__(self):
        return self.name

class PivotViewerItem(object):
    """
    Class to store PivotViewer items
    """
    def __init__(self,name, id, imageNumber, description, values = [], href = None):
        self.name = name
        self.id = id
        self.imageNumber = imageNumber
        self.description = description
        self.values = values
        self.href = href
    
    def __str__(self):
        return self.name

class PivotViewerCollectionCreator(object):
    """
    Class for creating PivotViewer collection from CSV files.
    """
    def loadFacetsFromCsv(self, path, header = True):
        file = csv.reader(open(path,'rb'))
        if header:
            header = file.next()
        facets = []
        for line in file:
            facet = PivotViewerFacet(line[0], line[1], bool(int(line[2])), 
                                     bool(int(line[3])), bool(int(line[4])))
            facets.append(facet)
        return(facets)
    
    def loadItemsFromCsv(self, path, header = True):
        file = csv.reader(open(path,'rb'))
        if header:
            header = file.next()
            hrefIndex = header.index("href")
            descriptionIndex = header.index("description")
            indexes = sorted([hrefIndex, descriptionIndex])
        items = []
        itemId = 0
        for line in file:
            values = list(line)
            del(values[indexes[1]])
            del(values[indexes[0]])
            item = PivotViewerItem(line[0], str(itemId), "#" + str(itemId), 
                                   line[descriptionIndex], values, line[hrefIndex])
            items.append(item)
            itemId = itemId + 1
        return(items)
    
    def createDeepZoomCollection(self, imageNames, imageFolder, collectionFolder):
        """ 
        Create DeepZoomCollection from jpg or png files.
        
        Arguments:
        imageNames -- list of image file names
        imageFolder -- path to the images folder
        collectionFolder -- folder into which the collection will be saved
        """
        #Create paths to image files from the folder
        imagePaths = []
        for image in imageNames:
            imagePaths.append(os.path.join(imageFolder, image))
        
        #Create paths to DeepZoom image files
        deepzoomImagePaths = list()
        for image in imageNames:
            deepzoomImagePath = os.path.join(collectionFolder, image)
            deepzoomImagePaths.append(deepzoomImagePath.rstrip(".jpgn") + ".xml")
        
        #Create DeepZoom images
        imageCreator = deepzoom.ImageCreator()       
        for imagePath, deepzoomImagePath in zip(imagePaths, deepzoomImagePaths):
            imageCreator.create(imagePath, deepzoomImagePath)
            
        #create DeepZoom collection
        os.chdir(collectionFolder)
        deepzoomImageNames = []
        for deepzoomImagePath in deepzoomImagePaths:
            deepzoomImageNames.append(os.path.split(deepzoomImagePath)[1])
        collectionCreator = deepzoom.CollectionCreator()
        collectionCreator.create(deepzoomImageNames, "collection.xml")
              
    
    def create(self, name, facetsCsv, itemsCsv, imageFolder, destination, deepZoomFolder = "deepzoom"):
        """
        Create PivotViewer collection.
        
        Arguments:
        facetsCsv -- CSV file specifying the PivotViewer facets.
        itemsCsv -- CSV file with the facet data.
        imageFolder -- folder containing the .jpg or .png images
        destination -- folder into which the PivotViewer collection will be created
        deepZoomFolder -- Location for DeepZoom images. Relative path from the destination folder.
        """
        #Create necessary paths
        deepZoomCollectionFolder = os.path.join(destination, deepZoomFolder)
        if not os.path.exists(deepZoomCollectionFolder):
            os.makedirs(deepZoomCollectionFolder)
        
        facets = self.loadFacetsFromCsv(facetsCsv)
        items = self.loadItemsFromCsv(itemsCsv)
        
        collection = PivotViewerCollection(name, facets, items, imgBase=os.path.join(deepZoomFolder, "collection.xml"))
        collection.save(os.path.join(destination, "collection.cxml"))
        
        #Extract image names from Collection items
        for i in range(len(facets)):
            if facets[i].name == "image_path":
                imagePathColumn = i
        
        imageNames = []
        for item in items:
            imageNames.append(item.values[imagePathColumn])
        
        #Create DeepZoom collection of the images
        self.createDeepZoomCollection(imageNames, imageFolder, deepZoomCollectionFolder)
            
####################################################################

def indent(elem, level=0):
    """
    Takes and ElementTree and indents it so that it looks good.
    
    Arguments:
        elem -- ElementTree object to be indented
        level -- 
    """
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

    
    