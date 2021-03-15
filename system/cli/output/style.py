from colored import fg, bg, attr

class Style:
    def __init__( self, text ):
        self.text = text
        self.style = list()

    def bold( self ):
        self.style.append(attr('bold'))
        return self

    def underlined( self ):
        self.style.append(attr('underlined'))
        return self

    def white( self ):
        self.style = [fg('white')]
        return self
    def light_gray( self ):
        self.style = [fg('light_gray')]
        return self
    def dark_gray( self ):
        self.style = [fg('dark_gray')]
        return self

    def red( self ):
        self.style.append(fg('red'))
        return self

    def green( self ):
        self.style = [fg('green')]
        return self

    def yellow( self ):
        self.style = [fg('yellow')]
        return self

    def blue( self ):
        self.style = [fg('blue')]
        return self

    def info( self ):
        return self.blue();

    def warning( self ):
        return self.yellow()

    def error( self ):
        return self.red()

    def success( self ):
        return self.green()

    def light( self ):
        return self.dark_gray()

    def apply_style( self, style=None ):
        if style is not None:
            if hasattr(self.__class__, style) and callable(getattr(self.__class__, style)):
                return getattr(self, style)()
        return self

    def __str__( self ) -> str:
        out = self.style
        out.append(self.text)
        out.append(attr('reset'))
        return "".join(out)

    def toString( self ):
        out = self.style
        out.append(self.text)
        out.append(attr('reset'))
        return "".join(out)

