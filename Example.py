import PivotViewer

#Define all necessary parameters
collectionName = "Cars"
facetsPath = "sample/sample_facets.csv"
dataPath = "sample/sample_data.csv"
imagesPath = "sample/sample_images"
collectionPath = "collection/"

#Create PivotViewer collection
collectionCreator = PivotViewer.PivotViewerCollectionCreator()
collectionCreator.create(collectionName,
                             facetsPath, 
                             dataPath,
                             imagesPath, 
                             collectionPath)