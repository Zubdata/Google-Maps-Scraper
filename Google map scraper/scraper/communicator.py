

class Communicator:

    __frontend_object = None
    __backend_object = None

    @classmethod
    def show_message(cls, message):
        if cls.__frontend_object is None:
            raise AttributeError("frontend_module attribute of Communicator class is none")
        
        cls.__frontend_object.messageshowing(message)

    @classmethod
    def show_error_message(cls, message, error_code):
        if cls.__frontend_object is None:
            raise AttributeError("frontend_module attribute of Communicator class is none")
        
        message = f"{message} Error code is: {error_code}"
        
        cls.__frontend_object.messageshowing(message)

    

    @classmethod
    def set_frontend_object(cls, frontend_object):
        cls.__frontend_object = frontend_object

    @classmethod
    def end_processing(cls):
        cls.__frontend_object.end_processing()

    @classmethod
    def get_output_format(cls):
        return cls.__frontend_object.outputFormatValue
    
    @classmethod
    def set_backend_object(cls, backend_object):
        cls.__backend_object = backend_object
    
    @classmethod
    def get_search_query(cls):
        return cls.__backend_object.searchquery