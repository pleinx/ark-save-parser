from dataclasses import dataclass

@dataclass
class GameObjectParserConfiguration:
    """
    Configuration for parsing game objects.
    
    Attributes:
        throw_exception_on_parse_error (bool): If True, throw an exception immediately when a game object can't be parsed.
                                               If False, skip the problematic game object.
        write_bin_file_on_parse_error (bool): If True, write a binary file when a parse error occurs.
    """
    throw_exception_on_parse_error: bool = False
    write_bin_file_on_parse_error: bool = False
