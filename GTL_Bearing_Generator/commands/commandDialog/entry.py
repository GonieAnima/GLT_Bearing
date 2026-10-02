import adsk.core
import os
from ...lib import fusionAddInUtils as futil
from ... import config
from .bearing import make_bearing
app = adsk.core.Application.get()
ui = app.userInterface


# TODO *** Specify the command identity information. ***
CMD_ID = f'{config.COMPANY_NAME}_{config.ADDIN_NAME}_bearing_generator'  # Unique ID for the command. This is used to reference the command and must be unique across all commands.
CMD_NAME = 'GTL Bearing Generator'                                  #Nombre de la caja de dialogo
CMD_Description = 'Generates a bearing based on the parameters provided by the user.'  # Description of the command that will be shown as a tooltip.

# Specify that the command will be promoted to the panel.
IS_PROMOTED = True

# TODO *** Define the location where the command button will be created. ***
# This is done by specifying the workspace, the tab, and the panel, and the 
# command it will be inserted beside. Not providing the command to position it
# will insert it at the end.
WORKSPACE_ID = 'FusionSolidEnvironment'
PANEL_ID = 'SolidScriptsAddinsPanel'
COMMAND_BESIDE_ID = 'ScriptsManagerCommand'

# Resource location for command icons, here we assume a sub folder in this directory named "resources".
ICON_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', '')

# Local list of event handlers used to maintain a reference so
# they are not released and garbage collected.
local_handlers = []


# Executed when add-in is run.
def start():
    # Create a command Definition.
    cmd_def = ui.commandDefinitions.addButtonDefinition(CMD_ID, CMD_NAME, CMD_Description, ICON_FOLDER)

    # Define an event handler for the command created event. It will be called when the button is clicked.
    futil.add_handler(cmd_def.commandCreated, command_created)

    # ******** Add a button into the UI so the user can run the command. ********
    # Get the target workspace the button will be created in.
    workspace = ui.workspaces.itemById(WORKSPACE_ID)

    # Get the panel the button will be created in.
    panel = workspace.toolbarPanels.itemById(PANEL_ID)

    # Create the button command control in the UI after the specified existing command.
    control = panel.controls.addCommand(cmd_def, COMMAND_BESIDE_ID, False)

    # Specify if the command is promoted to the main toolbar. 
    control.isPromoted = IS_PROMOTED


# Executed when add-in is stopped.
def stop():
    # Get the various UI elements for this command
    workspace = ui.workspaces.itemById(WORKSPACE_ID)
    panel = workspace.toolbarPanels.itemById(PANEL_ID)
    command_control = panel.controls.itemById(CMD_ID)
    command_definition = ui.commandDefinitions.itemById(CMD_ID)

    # Delete the button command control
    if command_control:
        command_control.deleteMe()

    # Delete the command definition
    if command_definition:
        command_definition.deleteMe()


# Function that is called when a user clicks the corresponding button in the UI.
# This defines the contents of the command dialog and connects to the command related events.
def command_created(args: adsk.core.CommandCreatedEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Created Event')

    # https://help.autodesk.com/view/fusion360/ENU/?contextId=CommandInputs
    inputs = args.command.commandInputs

    # TODO Define the dialog for your command by adding different inputs to the command.

    # Create a simple text box input.
    inputs.addTextBoxCommandInput('NombreRodamiento', 'Name', 'Bearing_x', 1, False) # id, name, default value, number of rows, is read only

    # Create a value input field and set the default using 1 unit of the default length unit.
    defaultLengthUnits = app.activeProduct.unitsManager.defaultLengthUnits  
    
    # Default values
    OuterDiameterOuterRing = adsk.core.ValueInput.createByString('30')
    OuterRing_Width = adsk.core.ValueInput.createByString('5')
    defaultODcorner = adsk.core.ValueInput.createByString('1')
    default_height = adsk.core.ValueInput.createByString('10')
    InnerRing_InnerDiameter = adsk.core.ValueInput.createByString('15')
    InnerRing_Width = adsk.core.ValueInput.createByString('5')
    defaultIRcorner = adsk.core.ValueInput.createByString('1')
    

    #imagen
    ruta_imagen = os.path.join(ICON_FOLDER, 'rodamiento.png')
    inputs.addImageCommandInput(
    'Diagram',   # id
    'Ex:',       # name on screen
    ruta_imagen
)
    # Pedir inputs de valor de rodamiento    
    inputs.addValueInput('OuterDiameter_Outer_ID', 'Outer ring diameter', defaultLengthUnits, OuterDiameterOuterRing)
    inputs.addValueInput('Width_Outer_ID', 'Outer ring width', defaultLengthUnits, OuterRing_Width)
    inputs.addValueInput('ODcorner_Outer_ID', 'Outer ring corner radius', defaultLengthUnits, defaultODcorner)
    inputs.addValueInput('Height', 'Height', defaultLengthUnits, default_height)
    inputs.addValueInput('InnerDiameter_Inner_ID', 'Inner ring diameter', defaultLengthUnits, InnerRing_InnerDiameter)
    inputs.addValueInput('Width_Inner_ID', 'Inner ring width', defaultLengthUnits, InnerRing_Width)
    inputs.addValueInput('IRcorner_Inner_ID', 'Inner ring corner radius', defaultLengthUnits, defaultIRcorner)



    # TODO Connect to the events that are needed by this command.
    futil.add_handler(args.command.execute, command_execute, local_handlers=local_handlers)
    futil.add_handler(args.command.inputChanged, command_input_changed, local_handlers=local_handlers)
    futil.add_handler(args.command.executePreview, command_preview, local_handlers=local_handlers)
    futil.add_handler(args.command.validateInputs, command_validate_input, local_handlers=local_handlers)
    futil.add_handler(args.command.destroy, command_destroy, local_handlers=local_handlers)


# This event handler is called when the user clicks the OK button in the command dialog or 
# is immediately called after the created event not command inputs were created for the dialog.
def command_execute(args: adsk.core.CommandEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Execute Event')

    # TODO ******************************** Your code here ********************************

    app = adsk.core.Application.get()
    ui = app.userInterface

    # Obtener el diseño actual
    design = adsk.fusion.Design.cast(app.activeProduct)

    if not design:
        ui.messageBox('No active design')
        return
    
############################## CREAR RODAMIENTO #####################################
    make_bearing(
        args.command.commandInputs.itemById('OuterDiameter_Outer_ID').value,
        args.command.commandInputs.itemById('Width_Outer_ID').value,
        args.command.commandInputs.itemById('Height').value,
        args.command.commandInputs.itemById('ODcorner_Outer_ID').value,
        args.command.commandInputs.itemById('InnerDiameter_Inner_ID').value,
        args.command.commandInputs.itemById('Width_Inner_ID').value,
        args.command.commandInputs.itemById('IRcorner_Inner_ID').value
    )

# This event handler is called when the command needs to compute a new preview in the graphics window.
def command_preview(args: adsk.core.CommandEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Preview Event')
    inputs = args.command.commandInputs


# This event handler is called when the user changes anything in the command dialog
# allowing you to modify values of other inputs based on that change.
def command_input_changed(args: adsk.core.InputChangedEventArgs):
    changed_input = args.input
    inputs = args.inputs

    # General logging for debug.
    futil.log(f'{CMD_NAME} Input Changed Event fired from a change to {changed_input.id}')


# This event handler is called when the user interacts with any of the inputs in the dialog
# which allows you to verify that all of the inputs are valid and enables the OK button.
def command_validate_input(args: adsk.core.ValidateInputsEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Validate Input Event')

    inputs = args.inputs
    
    # Validate the inputs that exist in this dialog. The bearing name is text,
    # so do not attempt to validate it as a numeric value.
    name_input = inputs.itemById('NombreRodamiento')
    if not name_input or not name_input.value.strip():
        args.areInputsValid = False
        

# This event handler is called when the command terminates.
def command_destroy(args: adsk.core.CommandEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Destroy Event')

    global local_handlers
    local_handlers = []
