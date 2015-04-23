uniform float u_time;
uniform vec2 u_input;
varying vec2 var_TexCoord;

void main()
{
	
	vec3 c;
	float l;
	float z = u_time;
	
	for (int i = 0; i < 3; i++)
	{
	        vec2 p = var_TexCoord;
		vec2 uv = p; 

		p -= (u_input + vec2(1.0)) * 0.5;
		p.x *= gl_FragCoord.x / gl_FragCoord.y;
		z += 0.07;
		l = length(p);
		
		uv += p / l * (sin(z) + 1.0) * abs(sin(l * 9.0 - z * 2.0));
		c[i] = 0.01 / length(abs(mod(uv, 1.0) - 0.5));
	}
	
	gl_FragColor = vec4(c / l, u_time);
}
