# Import data
import time
import numpy as np
import glob
import pydicom as dicom
import os

from skimage import io
from scipy.ndimage import zoom
from skimage.transform import  pyramid_gaussian

pt_path = '../Data/TD316'

def create_ct_volume( pt_path, prefix = 'CT'):
    dcms = glob.glob(os.path.join(pt_path, prefix+'*'))
    # dcms = glob.glob(os.path.join(pt_path, '0*.dcm'))
    slices = [dicom.read_file(dcm) for dcm in dcms]
    slices.sort(key=lambda x: float(x.ImagePositionPatient[2]))
    images = np.stack([ ((s.pixel_array * slices[0].RescaleSlope + slices[0].RescaleIntercept)) for s in slices],
                      axis=0).astype(np.float32)
    return (slices, images)



# vol = io.imread("https://s3.amazonaws.com/assets.datacamp.com/blog_assets/attention-mri.tif")
# volume = vol.T
slices, images = create_ct_volume(pt_path)
volume = zoom( images, (1,.23,.23), order=0)
# volume = images
r, c = volume[0].shape
nb_frames = volume.shape[0]

# Define frames
import plotly.graph_objects as go


#get patient list
pt_list = ['Data/TD315','Data/TD316']

# fig.show()
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

app = dash.Dash()
app.layout = html.Div([
    html.H1("Segmentation Preview"),
    html.H4("Choose a patient to display"),
    dcc.Dropdown(id='pt_list_dropdown_id',
            options = [ {'label':i, 'value': i} for i in pt_list],
            value = 'Data/TD314'),
    html.H4("Start slice"),
    dcc.Input(
        id="input_start_id",
        placeholder='start slice ...',
        type='number',
        value=0
    ),
    html.H4("End slice"),
    dcc.Input(
        id="input_end_id",
        placeholder='end slice ..',
        type='number',
        value = 1
    ),
    html.Button('Save', id='button_save_id', n_clicks=0),

    dcc.Graph(id = 'graph_id'),
    html.Div(id="status_id")    
])

#################
@app.callback(
    Output(component_id = "status_id", component_property="children"),
    [Input(component_id = 'button_save_id', component_property="n_clicks"),
     Input(component_id = 'pt_list_dropdown_id', component_property="value"),
     Input(component_id = 'input_start_id', component_property='value'),
     Input(component_id = 'input_end_id', component_property='value')
    ]
)
def save_slice_range(button_vl, pt, start, end):
    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if button_id == 'button_save_id':
        f = open('patient slice range.txt', 'a+')
        f.write("{}:{}:{}\n".format(pt, start, end))
        f.close()
    return "{}:{}:{}".format(pt, start, end)

##########3
@app.callback(
    Output(component_id = 'graph_id', component_property='figure'),
    [Input(component_id = 'pt_list_dropdown_id', component_property='value')]
)
def update_graph(pt_path):
    # global volume
    # global nb_frames
    # global r,c

    slices, images = create_ct_volume(pt_path)
    volume = zoom( images, (1,.23,.23), order=0)
    # volume = images
    r, c = volume[0].shape
    nb_frames = volume.shape[0]

    fig = go.Figure(frames=[go.Frame(data=go.Surface(
        z=((nb_frames-1) - k) * np.ones((r, c)),
        surfacecolor=np.flipud(volume[nb_frames - 1 - k]),
        cmin=-100, cmax=400
        ),
        name=str(k) # you need to name the frame for the animation to behave properly
        )
        for k in range(nb_frames)])

# Add data to be displayed before animation starts
    fig.add_trace(go.Surface(
        z=(nb_frames-1) * np.ones((r, c)),
        surfacecolor=np.flipud(volume[nb_frames-1]),
        colorscale='Gray',
        cmin=-100, cmax=400,
        colorbar=dict(thickness=20, ticklen=4)
        ))


    def frame_args(duration):
        return {
                "frame": {"duration": duration},
                "mode": "immediate",
                "fromcurrent": True,
                "transition": {"duration": duration, "easing": "linear"},
            }

    sliders = [
            {
                "pad": {"b": 10, "t": 60},
                "len": 0.9,
                "x": 0.1,
                "y": 0,
                "steps": [
                    {
                        "args": [[f.name], frame_args(0)],
                        "label": str(k),
                        "method": "animate",
                    }
                    for k, f in enumerate(fig.frames)
                ],
            }
        ]

    # Layout
    fig.update_layout(
         title='3D Slices in volume',
         width=800,
         height=800,
         scene=dict(
                    zaxis=dict(range=[-0.1, nb_frames], autorange=False),
                    aspectratio=dict(x=1, y=1, z=1),
                    ),
         updatemenus = [
            {
                "buttons": [
                    {
                        "args": [None, frame_args(50)],
                        "label": "&#9654;", # play symbol
                        "method": "animate",
                    },
                    {
                        "args": [[None], frame_args(0)],
                        "label": "&#9724;", # pause symbol
                        "method": "animate",
                    },
                ],
                "direction": "left",
                "pad": {"r": 10, "t": 70},
                "type": "buttons",
                "x": 0.1,
                "y": 0,
            }
         ],
         sliders=sliders
)



    return fig

app.run_server(host='0.0.0.0', debug=True)