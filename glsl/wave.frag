#define PI 3.14159265359
vec3 COLOR = vec3(0.3, 0.1, 0.2);

uniform float u_time;
uniform vec2 u_input;
varying vec2 var_TexCoord;

void main()
{
    
    vec2 uv = var_TexCoord;
    
    // accumulator
    vec3 c = vec3(0.0);
    
    float x = 0.3 * uv.x;
    float t = mod(u_time, 2.0 * PI) * 0.05;
    
    for (float i = 0.0; i < 0.5; i += 0.025)
    {
        float nx = x + 2.0 * i;
    	float y = pow(nx, 3.0) + sin(40.0 * i + t*100.0) * (u_input.x * 0.5);
        float t = pow((y - uv.y), 0.1) * 1.05;
        
        c += (COLOR * (1.0 - t));
    }
   
    
 	
    gl_FragColor = vec4(c, 1.0);
}
