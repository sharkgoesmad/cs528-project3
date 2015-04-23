#version 130
varying vec2 var_TexCoord;
uniform int u_Visibility[512];

const int PACK_DEPTH = 31;

int getIdx()
{
        return int(gl_Color.z) * 255 + int(gl_Color.w);
}


int isVisible(int idx)
{
	int i = idx / PACK_DEPTH;
        int pos = idx % PACK_DEPTH;    
        
        int v = u_Visibility[i] >> pos;	
        
        return v % 2;
}


void main(void)
{
	gl_Position = ftransform();

	// vertex should be hidden
	gl_Position.w *= float(isVisible( getIdx() ));
	
	gl_FrontColor = gl_Color;
}
