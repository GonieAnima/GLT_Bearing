import adsk.core
import adsk.fusion

def make_bearing(OuterRing_OuterDiameter, OuterRing_Width, Height, ODcorner, InnerRing_Bore, InnerRing_Width, IRcorner):

    app = adsk.core.Application.get()
    ui = app.userInterface
    design = adsk.fusion.Design.cast(app.activeProduct)
    
    if not design:
        return

    # Componente raíz
    rootComp = design.rootComponent
    
    # Crear componente Rodamiento
    ocurrenciaRodamiento = rootComp.occurrences.addNewComponent(
        adsk.core.Matrix3D.create()
    )
    
    # Obtener el componente que acabamos de crear
    rodamiento = ocurrenciaRodamiento.component
    rodamiento.name = 'New bearing'  # Nombre del componente

    ############################################################
    # Crear un nuevo componente dentro del componente Rodamiento
    ############################################################

    ocurrenciaExterior = rodamiento.occurrences.addNewComponent(
        adsk.core.Matrix3D.create()
    )
    aroExterior = ocurrenciaExterior.component
    aroExterior.name = 'Outer Ring'
    
    # Crear sketch en el aro exterior
    sketchExterior = aroExterior.sketches.add(
    aroExterior.xYConstructionPlane
    )
    sketchExterior.name = 'Outer Ring Sketch'

    #Crear circulo exterior
    circles = sketchExterior.sketchCurves.sketchCircles     #Acceder a herramienta de circulos
    
    #Dibujar circulo exterior
    circuloExterior = circles.addByCenterRadius(
        adsk.core.Point3D.create(0, 0, 0),  # Centro del circulo
        OuterRing_OuterDiameter / 2                   # Radio del circulo
    )
    #Dibujar circulo interior
    circuloInterior = circles.addByCenterRadius(
            adsk.core.Point3D.create(0, 0, 0),  # Centro del circulo
            OuterRing_OuterDiameter / 2 - OuterRing_Width                   # Radio del circulo
        )

    # Extruir el aro exterior
    prof = sketchExterior.profiles.item(0)  # Obtener el perfil del sketch
    extrudes = aroExterior.features.extrudeFeatures
    extInput = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    distance = adsk.core.ValueInput.createByReal(Height)  # Distancia de extrusión
    extInput.setDistanceExtent(False, distance)
    extrude = extrudes.add(extInput)
    extrude.bodies.item(0).name = 'Outer Ring Body'  # Nombre del cuerpo extruido

    # CHAMFER
    # Colección de aristas de la cara superior
    chamferEdges = adsk.core.ObjectCollection.create()

    body = extrude.bodies.item(0)

    for i in range(body.edges.count):
        chamferEdges.add(body.edges.item(i))

    # Crear el chaflán
    chamfers = aroExterior.features.chamferFeatures

    chamferInput = chamfers.createInput2()

    distance = adsk.core.ValueInput.createByReal(ODcorner)

    chamferInput.chamferEdgeSets.addEqualDistanceChamferEdgeSet(
        chamferEdges,
        distance,
        False
    )

    chamfer = chamfers.add(chamferInput)

    if not chamfer:
        ui.messageBox('Fusion no ha podido crear el chaflán')
    else:
        chamfer.name = 'Outer Ring Chamfer'

    ############################################################
    # Crear un nuevo componente dentro del componente Rodamiento
    ############################################################

    ocurrenciaInterior = rodamiento.occurrences.addNewComponent(
        adsk.core.Matrix3D.create()
    )
    
    aroInterior = ocurrenciaInterior.component
    aroInterior.name = 'Inner Ring'

    # Crear sketch en el aro interior
    sketchInterior = aroInterior.sketches.add(
        aroInterior.xYConstructionPlane
    )
    sketchInterior.name = 'Inner Ring Sketch'

    #Crear circulo exterior
    circles2 = sketchInterior.sketchCurves.sketchCircles     #Acceder a herramienta de circulos
    
    #Dibujar circulo exterior
    circuloExteriorInner = circles2.addByCenterRadius(
        adsk.core.Point3D.create(0, 0, 0),  # Centro del circulo
        InnerRing_Bore / 2                   # Radio del circulo
    )
    #Dibujar circulo interior
    circuloInteriorInner = circles2.addByCenterRadius(
            adsk.core.Point3D.create(0, 0, 0),  # Centro del circulo
            InnerRing_Bore / 2 + InnerRing_Width                   # Radio del circulo
        )
    
    # Extruir el aro interior
    prof = sketchInterior.profiles.item(1)  # Obtener el perfil del sketch
    extrudes = aroInterior.features.extrudeFeatures
    extInput = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    distance = adsk.core.ValueInput.createByReal(Height)  # Distancia de extrusión
    extInput.setDistanceExtent(False, distance)
    extrude = extrudes.add(extInput)
    extrude.bodies.item(0).name = 'Inner Ring Body'  # Nombre del cuerpo extruido

    # CHAMFER INNER RING
    # Colección de todas las aristas
    chamferEdges = adsk.core.ObjectCollection.create()

    body = extrude.bodies.item(0)

    # Añadir TODAS las aristas del Inner Ring
    for i in range(body.edges.count):
        chamferEdges.add(body.edges.item(i))

    # Crear el chaflán
    chamfers = aroInterior.features.chamferFeatures

    chamferInput = chamfers.createInput2()

    # Distancia del chaflán
    distance = adsk.core.ValueInput.createByReal(IRcorner)

    chamferInput.chamferEdgeSets.addEqualDistanceChamferEdgeSet(
        chamferEdges,
        distance,
        False
    )

    # Crear chaflán
    chamfer = chamfers.add(chamferInput)

    if not chamfer:
        ui.messageBox('Fusion no ha podido crear el chaflán del Inner Ring')
    else:
        chamfer.name = 'Inner Ring Chamfer'

    # Ya creado el rodamiento interno y externo
    