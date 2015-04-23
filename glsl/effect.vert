varying vec2 var_TexCoord;

void main(void)
{
	gl_Position = ftransform();
	var_TexCoord = gl_MultiTexCoord0.xy;
}
