# version 130 // required to use OpenGL core standard

//=== 'in' attributes are passed on from the vertex shader's 'out' attributes, and interpolated for each fragment
in vec3 fragment_color;        // the fragment colour
in vec3 position_view_space;   // the position in view coordinates of this fragment
in vec3 normal_view_space;     // the normal in view coordinates to this fragment
in vec2 fragment_texCoord;

//=== 'out' attributes are the output image, usually only one for the colour of each pixel
out vec4 final_color;

//=== uniforms
uniform int mode;	// the rendering mode (better to code different shaders!)
uniform int has_texture;
uniform sampler2D textureObject; // texture object
uniform sampler2DShadow shadow_map;

// shadow map matrix
// this shadow map matrix times the fragment shader position allows looking up the depth in the shadow map texture
uniform mat4 shadow_map_matrix;

// material uniforms
uniform vec3 Ka;    // ambient reflection properties of the material
uniform vec3 Kd;    // diffuse reflection propoerties of the material
uniform vec3 Ks;    // specular properties of the material
uniform float Ns;   // specular exponent

// light source
uniform vec3 light; // light position in view space
uniform vec3 Ia;    // ambient light properties
uniform vec3 Id;    // diffuse properties of the light source
uniform vec3 Is;    // specular properties of the light source

uniform float alpha = 1.0f;


vec4 phong(vec4 texval);

vec4 phong(vec4 texval) {
    // calculate vectors used for shading calculations
    vec3 camera_direction = -normalize(position_view_space);
    vec3 light_direction = normalize(light-position_view_space);

    // calculate light components
    vec4 ambient = vec4(Ia*Ka,alpha);
    vec4 diffuse = vec4(Id*Kd*max(0.0f,dot(light_direction, normal_view_space)), alpha);
    vec4 specular = vec4(Is*Ks*pow(max(0.0f, dot(reflect(light_direction, normal_view_space), -camera_direction)), Ns), alpha);

    // calculate the attenuation function
    // in this formula, dist should be the distance between the surface and the light
    float dist = length(light - position_view_space);
    float attenuation =  min(1.0/(dist*dist*0.005) + 1.0/(dist*0.05), 1.0);

    // combine the shading components
    return texval*ambient + attenuation*(texval*diffuse + specular);
}

///=== main shader code
void main() {

    // sample from the texture map
    // the texture2D function just samples from the texture object at coordinates set by fragment_texCoord
    // using interpolation/extrapolation as set in the OpenGL program
    vec4 texval = vec4(1.0f);
    if(has_texture == 1)
        texval = texture2D(textureObject, fragment_texCoord);

    final_color = vec4(0.0f);

    // combine the shading components

    final_color = phong(texval);

    vec4 p = shadow_map_matrix*vec4(position_view_space, 1);

	if (p.w > 0)
	{
		p.xyz /= p.w;

		p.z *= 0.999;

		float val = texture(shadow_map, p.xyz);
        final_color.xyz = (1.0-val)*Ka*Ia*texval.xyz + val*final_color.xyz;
	}
}


