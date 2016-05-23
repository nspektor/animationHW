"""========== script.py ==========

  This is the only file you need to modify in order
  to get a working mdl project (for now).

  my_main.c will serve as the interpreter for mdl.
  When an mdl script goes through a lexer and parser,
  the resulting operations will be in the array op[].

  Your job is to go through each entry in op and perform
  the required action from the list below:

  frames: set num_frames for animation

  basename: set name for animation

  vary: manipluate knob values between two given frames
        over a specified interval

  set: set a knob to a given value

  setknobs: set all knobs to a given value

  push: push a new origin matrix onto the origin stack

  pop: remove the top matrix on the origin stack

  move/scale/rotate: create a transformation matrix
                     based on the provided values, then
		     multiply the current top of the
		     origins stack by it.

  box/sphere/torus: create a solid object based on the
                    provided values. Store that in a
		    temporary matrix, multiply it by the
		    current top of the origins stack, then
		    call draw_polygons.

  line: create a line based on the provided values. Store
        that in a temporary matrix, multiply it by the
	current top of the origins stack, then call draw_lines.

  save: call save_extension with the provided filename

  display: view the image live

  jdyrlandweaver
  ========================="""



import mdl
from display import *
from matrix import *
from draw import *



"""======== first_pass( commands, symbols ) ==========

  Checks the commands array for any animation commands
  (frames, basename, vary)

  Should set num_frames and basename if the frames
  or basename commands are present

  If vary is found, but frames is not, the entire
  program should exit.

  If frames is found, but basename is not, set name
  to some default value, and print out a message
  with the name being used.

  jdyrlandweaver
  ==================== """
basename = "default_img"
def first_pass( commands ):
    global basename
    if "basename" in commands:
        basename = commands[ commands.index("basename") ][0]
    else:
        print "Using default basename: " + basename
    if "vary" in commands:
        if commands.count("frame") != 1:
            #error!!
            print "you suck"
            exit()
        else:
            num_frames = commands[ commands.index("frames")][0]
            return second_pass(commands, num_frames)
    else:
       return second_pass(commands, 1) #if no vary, just one frame img?



"""======== second_pass( commands ) ==========

  In order to set the knobs for animation, we need to keep
  a seaprate value for each knob for each frame. We can do
  this by using an array of dictionaries. Each array index
  will correspond to a frame (eg. knobs[0] would be the first
  frame, knobs[2] would be the 3rd frame and so on).

  Each index should contain a dictionary of knob values, each
  key will be a knob name, and each value will be the knob's
  value for that frame.

  Go through the command array, and when you find vary, go
  from knobs[0] to knobs[frames-1] and add (or modify) the
  dictionary corresponding to the given knob with the
  appropirate value.
  ===================="""
def second_pass( commands, num_frames ):
    knobs = []
    for n in xrange(num_frames):
        knobs.append({})

    for c in commands:
        if c[0] == "vary":
            for n in range(num_frames):
                f_start=c[2]
                f_end=c[3]
                val_start=c[4]
                val_end=c[5]
                knob_name=c[1]
                knob_val=1
                if n<f_start:
                    knobs[n][knob_name]=val_start
                elif n>f_end: #animation already ended
                    knobs[n][knob_name]=val_end
                else:
                    knob_val = val_start + ( (val_end - val_start)*(n - f_start) / float((f_end - f_start)))
                    knobs[n][knob_name]=knob_val
    print knobs
    return knobs

def run(filename):
    """
    This function runs an mdl script
    """
    color = [255, 255, 255]
    tmp = new_matrix()
    ident( tmp )

    p = mdl.parseFile(filename)


    if p:
        (commands, symbols) = p
    else:
        print "Parsing failed."
        return
    stack = [ tmp ]
    screen = new_screen()
    knobs = first_pass(commands) #which calls second pass
    f = 0
    while ( f <= len(knobs) ):
        for command in commands:
            if command[0] == "pop":
                stack.pop()
                if not stack:
                    stack = [ tmp ]
            if command[0] == "push":
                stack.append( stack[-1][:] )
            if command[0] == "save":
                save_extension(screen, command[1])
            if command[0] == "display":
                display(screen)
            if command[0] == "sphere":
                m = []
                args = [command[x] if command[x] not in knobs[f] else knobs[f][x] for x in range(5)+1 ]
                add_sphere(m, args[1], args[2], args[3], args[4], 5)
                matrix_mult(stack[-1], m)
                draw_polygons( m, screen, color )

            if command[0] == "torus":
                m = []
                args = [command[x] if command[x] not in knobs[f] else knobs[f][x] for x in range(5)+1 ]
                add_torus(m, args[1], args[2], args[3], args[4], args[5], 5)
                matrix_mult(stack[-1], m)
                draw_polygons( m, screen, color )

            if command[0] == "box":
                m = []
                args = [command[x] if command[x] not in knobs[f] else knobs[f][x] for x in range(len(command))+1 ]
                add_box(m, *args[1:])
                matrix_mult(stack[-1], m)
                draw_polygons( m, screen, color )

            if command[0] == "line":
                m = []
                args = [command[x] if command[x] not in knobs[f] else knobs[f][x] for x in range(len(command))+1 ]
                add_edge(m, *args[1:])
                matrix_mult(stack[-1], m)
                draw_lines( m, screen, color )

            if command[0] == "bezier":
                m = []
                args = [command[x] if command[x] not in knobs[f] else knobs[f][x] for x in range(8)+1 ]
                add_curve(m, args[1], args[2], args[3], args[4], args[5], args[6], args[7], args[8], .05, 'bezier')
                matrix_mult(stack[-1], m)
                draw_lines( m, screen, color )

            if command[0] == "hermite":
                m = []
                args = [command[x] if command[x] not in knobs[f] else knobs[f][x] for x in range(8)+1 ]
                add_curve(m, args[1], args[2], args[3], args[4], args[5], args[6], args[7], args[8], .05, 'hermite')
                matrix_mult(stack[-1], m)
                draw_lines( m, screen, color )

            if command[0] == "circle":
                m = []
                args = [command[x] if command[x] not in knobs[f] else knobs[f][x] for x in range(4)+1 ]
                add_circle(m, args[1], args[2], args[3], args[4], .05)
                matrix_mult(stack[-1], m)
                draw_lines( m, screen, color )

            if command[0] == "move":
                xval = command[1]
                yval = command[2]
                zval = command[3]

                t = make_translate(xval, yval, zval)
                matrix_mult( stack[-1], t )
                stack[-1] = t

            if command[0] == "scale":
                xval = command[1]
                yval = command[2]
                zval = command[3]

                t = make_scale(xval, yval, zval)
                matrix_mult( stack[-1], t )
                stack[-1] = t

            if command[0] == "rotate":
                angle = command[2] * (math.pi / 180)

                if command[1] == 'x':
                    t = make_rotX( angle )
                elif command[1] == 'y':
                    t = make_rotY( angle )
                elif command[1] == 'z':
                    t = make_rotZ( angle )

                matrix_mult( stack[-1], t )
                stack[-1] = t
            save_extension(screen, basename+"0"+str(f)+".png")
            clear_screen(screen)
            f += 1 #onto the next frame
