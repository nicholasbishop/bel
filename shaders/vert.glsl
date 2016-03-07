attribute vec4 vert_loc;
 
/* uniform mat4 model_view; */
/* uniform mat4 projection; */

varying vec4 color;
 
void main() {
    /* vec4 p = model_view * vec4(vert_loc.x, vert_loc.y, vert_loc.z, 1.0); */
	/* if (vert_loc.w == 1.0) { */
	/* 	color = vec4(1, 0, 0, 1); */
	/* } else if (vert_loc.w == 2.0) { */
	/* 	color = vec4(0, 1, 0, 1); */
	/* } else { */
	/* 	color = vec4(0, 0, 1, 1); */
	/* } */
    /* gl_Position = projection * p; */
	color = vec4(1, 0, 0, 1);
	if (vert_loc.x == 0.0) {
		gl_Position = vec4(0.2, 0.0, 0.0, 1.0);
	} else {
		//gl_Position = vec4(0.1, 0, 0, 1);
		gl_Position = vec4(0.0, 0.2, 0.0, 1.0);
	}
	/* if (vert_loc.w <= 1.0) { */
	/* 	gl_Position = vec4(-0.5, -0.5, 0, 1); */
	/* } else if (vert_loc.w <= 2.0) { */
	/* 	gl_Position = vec4(0.5, -0.5, 0, 1); */
	/* } else if (vert_loc.w <= 3.0) { */
	/* 	gl_Position = vec4(0.5, 0.5, 0, 1); */
	/* } else { */
	/* 	gl_Position = vec4(0, 0, 0, 1); */
	/* } */
}
