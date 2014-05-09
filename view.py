# -----------------------------------------------------------------------------
#  A Galaxy Simulator based on the density wave theory
#  (c) 2012 Ingo Berg
#
#  Simulating a Galaxy with the density wave theory
#  http://beltoforion.de/galaxy/galaxy_en.html
#
#  Python version(c) 2014 Nicolas P.Rougier
# -----------------------------------------------------------------------------
import numpy as np

from galaxy import Galaxy
from vispy import gloo
from vispy.app import Canvas
from vispy.util.transforms import perspective, translate


vertex = """
#version 120
uniform mat4  u_model;
uniform mat4  u_view;
uniform mat4  u_projection;
uniform sampler2D u_colormap;

attribute float a_size;
attribute float a_type;
attribute vec2  a_position;
attribute float a_temperature;
attribute float a_brightness;


varying vec3 v_color;

void main (void) {
    gl_Position = u_projection * u_view * u_model * vec4(a_position,0.0,1.0);
    gl_PointSize = a_size;
    v_color = texture2D(u_colormap, vec2(a_temperature,.5)).rgb * a_brightness/1.75;
    if (a_type == 2)
        v_color *= vec3(2,1,1);
    else if (a_type == 3)
        v_color = vec3(.9);
}
"""

fragment = """
#version 120
uniform sampler2D u_texture;
varying vec3 v_color;
void main()
{
    gl_FragColor = texture2D(u_texture, gl_PointCoord);
    gl_FragColor.rgb *= v_color;
}
"""


class GalaxyCanvas(Canvas):
    def __init__(self):
        Canvas.__init__(self, size=[800, 800], close_keys='ESCAPE', show=True,
                        title='Galaxy')
        self.galaxy = Galaxy(35000)
        self.galaxy.reset(13000, 4000, 0.0004, 0.90, 0.90, 0.5, 200, 300)
        program = gloo.Program(vertex, fragment, count=len(self.galaxy))
        view = np.eye(4, dtype=np.float32)
        translate(view, 0, 0, -5)
        program['u_view'] = view
        program['u_model'] = np.eye(4, dtype=np.float32)
        program['u_projection'] = np.eye(4, dtype=np.float32)

        from PIL import Image
        from specrend import (SMPTEsystem, spectrum_to_xyz, norm_rgb,
                              xyz_to_rgb, bb_spectrum)
        image = Image.open("particle.bmp")
        program['u_texture'] = np.array(image)/255.0
        t0 = 1000.
        t1 = 10000.
        n = 256
        dt = (t1 - t0) / n
        colors = np.zeros((1, n, 3), dtype=np.float32)
        for i in range(n):
            cs = SMPTEsystem
            temperature = t0 + i*dt
            x, y, z = spectrum_to_xyz(bb_spectrum, temperature)
            r, g, b = xyz_to_rgb(cs, x, y, z)
            colors[0, i] = norm_rgb(r, g, b)
        program['u_colormap'] = gloo.Texture2D(colors)
        program['a_size'] = self.galaxy['size']
        program['a_type'] = self.galaxy['type']
        self.program = program

    def on_initialize(self):
        gloo.set_clear_color((0.0, 0.0, 0.0, 1.0))
        gloo.set_state(blend=True, depth_test=True,
                       blend_func=('src_alpha', 'one_minus_src_alpha'))

    def on_paint(self, region):
        self.galaxy.update(100000)  # in years !
        self.program['a_size'] = self.galaxy['size']
        gloo.clear()
        t0 = 1000.
        t1 = 10000.
        gloo.set_state(blend=True, blend_func=('src_alpha', 'one'))
        self.program['a_position'] = self.galaxy['position'] / 15000.0
        self.program['a_temperature'] = ((self.galaxy['temperature'] - t0)
                                         / (t1-t0))
        self.program['a_brightness'] = self.galaxy['brightness']
        self.program.draw('points')

    def on_resize(self, width, height):
        gloo.set_viewport(0, 0, width, height)
        projection = perspective(45.0, width / float(height), 1.0, 1000.0)
        self.program['u_projection'] = projection

if __name__ == '__main__':
    c = GalaxyCanvas()
    c.app.run()
