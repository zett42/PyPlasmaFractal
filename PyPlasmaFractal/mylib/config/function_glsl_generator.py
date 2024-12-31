from .function_registry import FunctionInfo, FunctionParam, ParamType


class GlslTypeMapper:
    """
    A class used to map custom parameter types to their corresponding GLSL types.
    """ 
   
    @staticmethod
    def get_glsl_type(param_type: ParamType) -> str:
        """
        Gets the GLSL type corresponding to the given ParamType.
        """        
        match param_type:
            case ParamType.FLOAT:
                return "float"
            case ParamType.COLOR:
                return "vec4"
            case _:
                raise ValueError(f"Unsupported param type: {param_type}")


class GlslGenerator:
    """
    A class used to generate GLSL code related to functions.   
    """
    
    @staticmethod
    def get_uniform_name(param_name: str) -> str:
        """
        Generates the uniform name for the given parameter name.
        """
        return f"u_{param_name}"
    

    @staticmethod
    def get_function_params_uniform_names(function: FunctionInfo) -> list[str]:
        """
        Generates a list of uniform names for the given function's parameters.
        """
        return [GlslGenerator.get_uniform_name(p.name) for p in function.params]

    
    @staticmethod
    def generate_param_uniform(param: FunctionParam) -> str:
        """
        Generates a GLSL uniform declaration from the given parameter.
        """
        glsl_type = GlslTypeMapper.get_glsl_type(param.param_type)
        return f"uniform {glsl_type} {GlslGenerator.get_uniform_name(param.name)};"
       
   
    @staticmethod
    def generate_function_params_uniforms(function: FunctionInfo) -> str:
        """
        Generates GLSL uniform declarations from the given function's parameters.
        """
        return "\n".join(GlslGenerator.generate_param_uniform(p) for p in function.params)
    
    
    @staticmethod
    def generate_function_args(function: FunctionInfo, initial_comma: bool = False) -> str:
        """
        Generates a string of function arguments to pass to the given function.
        """
        args = ", ".join(GlslGenerator.get_uniform_name(p.name) for p in function.params)
        if args and initial_comma:
            return f", {args}"
        return args
