from .style import Style
class Item():
    def __init__( self, label, value, style=None, display_label=True, padding=None, format='{0}' ):
        self.label = label
        self.value = value
        self.display_label = display_label
        self.style = style
        self.format = format

    def error( self ):
        self.style = "error"
        return self

    def success( self ):
        self.style = "success"
        return self

    def warning( self ):
        self.style = "warning"
        return self

    def info( self ):
        self.style = "info"
        return self

    def bold( self ):
        self.style = "bold"
        return self

    def light( self ):
        self.style = "light"
        return self

    def underlined( self ):
        self.style = "underlined"
        return self

    def conditionalStyle( self, condition, true_style, false_style ):

        self.style = true_style if condition else false_style
        return self

    def __repr__( self ):

        parts = list()

        if self.display_label:
            parts.append(Style(self.label).light().toString())

        value = self.value
        if type(self.format) is list:
            for frmt in self.format:
                value = str(frmt).format(value)
        else:
            value = self.format.format(value)

        value = Style(value).apply_style(self.style).toString()
        parts.append(value)

        return ": ".join(parts)

