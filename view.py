# -----------------------------------------------------------------------------
#  A Galaxy Simulator based on the density wave theory
#  (c) 2012 Ingo Berg
#
#  Simulating a Galaxy with the density wave theory
#  http://beltoforion.de/galaxy/galaxy_en.html
#
#  Python version(c) 2014 Nicolas P.Rougier
# -----------------------------------------------------------------------------
import sys
import numpy as np
import OpenGL.GL as gl
import OpenGL.GLUT as glut

from galaxy import Galaxy
from vispy import gloo
from vispy.util.transforms import perspective, translate, rotate


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

def display():
    gl.glClear(gl.GL_COLOR_BUFFER_BIT)
    t0 = 1000.
    t1 = 10000.
    gl.glEnable(gl.GL_BLEND);
    gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE);
    program['a_position']    = galaxy['position'] / 15000.0
    program['a_temperature'] = (galaxy['temperature'] - t0) / (t1-t0)
    program['a_brightness']  = galaxy['brightness']
    program.draw(gl.GL_POINTS)

    glut.glutSwapBuffers()

def reshape(width, height):
    gl.glViewport(0, 0, width, height)
    projection = perspective(45.0, width / float(height), 1.0, 1000.0)
    program['u_projection'] = projection

def keyboard(key, x, y):
    if key == '\033': sys.exit()

def timer(fps):
    galaxy.update(100000) # in years !
    program['a_size'] = galaxy['size']
    glut.glutTimerFunc(1000 / fps, timer, fps)
    glut.glutPostRedisplay()


galaxy = Galaxy(35000)
galaxy.reset(13000, 4000, 0.0004, 0.90, 0.90, 0.5, 200, 300)

glut.glutInit(sys.argv)
glut.glutInitDisplayMode(glut.GLUT_DOUBLE | glut.GLUT_RGBA)
glut.glutCreateWindow('Galaxy')
glut.glutReshapeWindow(800,800)
glut.glutReshapeFunc(reshape)
glut.glutKeyboardFunc(keyboard)
glut.glutDisplayFunc(display)
glut.glutTimerFunc(1000 / 60, timer, 60)

program = gloo.Program(vertex, fragment, count = len(galaxy))
view = np.eye(4, dtype=np.float32)
model = np.eye(4, dtype=np.float32)
projection = np.eye(4, dtype=np.float32)
translate(view, 0, 0, -5)
program['u_model'] = model
program['u_view'] = view

from PIL import Image
image = Image.open("particle.bmp")
program['u_texture'] = np.array(image)/255.0

from specrend import *

t0 = 1000.
t1 = 10000.
n = 256
dt =  (t1-t0)/n
colors = np.zeros((1,n,3), dtype=np.float32)
for i in range(n):
    cs = SMPTEsystem
    temperature = t0 + i*dt
    x,y,z = spectrum_to_xyz(bb_spectrum, temperature)
    r,g,b = xyz_to_rgb(cs, x, y, z)
    colors[0,i] = norm_rgb(r, g, b)
program['u_colormap'] = gloo.Texture2D(colors)
program['a_size'] = galaxy['size']
program['a_type'] = galaxy['type']



# OpenGL initalization
# --------------------------------------
gl.glClearColor(0.0, 0.0, 0.0, 1.0)
gl.glEnable(gl.GL_BLEND)
gl.glEnable(gl.GL_DEPTH_TEST)
gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
gl.glEnable(gl.GL_VERTEX_PROGRAM_POINT_SIZE)
gl.glEnable(gl.GL_POINT_SPRITE)

# Start
# --------------------------------------
glut.glutMainLoop()
