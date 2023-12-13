import os
import vtk
import cv2
import numpy as np


def extract_obstacle_properties(image_path):
    # Charger l'image
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    # Configuration des paramètres
    # Couleur des obstacles (blanc dans une image en niveaux de gris)
    obstacle_color = 255
    threshold = 200  # Seuil pour binariser l'image

    # Binarisation de l'image
    _, binary_image = cv2.threshold(image, threshold, 255, cv2.THRESH_BINARY)

    # Initialiser le renderer VTK
    renderer = vtk.vtkRenderer()

    # Configuration des paramètres pour mapper l'image
    image_data = vtk.vtkImageData()
    image_data.SetDimensions(binary_image.shape[1], binary_image.shape[0], 1)
    image_data.AllocateScalars(vtk.VTK_UNSIGNED_CHAR, 1)

    # Remplir les données de l'image
    for i in range(binary_image.shape[0]):
        for j in range(binary_image.shape[1]):
            image_data.SetScalarComponentFromFloat(
                j, binary_image.shape[0] - 1 - i, 0, 0, binary_image[i, j])

    # Mapper l'image
    image_mapper = vtk.vtkImageMapper()
    image_mapper.SetInputData(image_data)
    image_actor = vtk.vtkActor2D()
    image_actor.SetMapper(image_mapper)
    renderer.AddActor(image_actor)

    # Initialiser le contour
    contour_filter = vtk.vtkMarchingSquares()
    contour_filter.SetInputData(image_data)
    contour_filter.SetValue(0, obstacle_color)

    # Mapper le contour
    contour_mapper = vtk.vtkPolyDataMapper()
    contour_mapper.SetInputConnection(contour_filter.GetOutputPort())

    # Actor pour afficher le contour
    contour_actor = vtk.vtkActor()
    contour_actor.SetMapper(contour_mapper)
    contour_actor.GetProperty().SetColor(1, 0, 0)  # Couleur rouge

    # Ajouter le contour au renderer
    renderer.AddActor(contour_actor)

    # Configurer la fenêtre de rendu
    render_window = vtk.vtkRenderWindow()
    render_window.SetWindowName("CSO Obstacle Extraction")
    render_window.SetSize(800, 800)
    render_window.AddRenderer(renderer)

    # Configurer le rendu interactif
    render_window_interactor = vtk.vtkRenderWindowInteractor()
    render_window_interactor.SetRenderWindow(render_window)

    # Définir les propriétés de la caméra
    renderer.GetActiveCamera().ParallelProjectionOn()
    renderer.GetActiveCamera().SetPosition(0, 0, 1)
    renderer.GetActiveCamera().SetFocalPoint(0, 0, 0)
    renderer.GetActiveCamera().SetViewUp(0, -1, 0)

    # Initialiser le renderer et mapper pour les contours des obstacles
    render_window.Render()
    render_window_interactor.Start()


# Appel de la fonction avec le chemin de l'image en argument
extract_obstacle_properties(f"{os.getcwd()}/plan.png")
