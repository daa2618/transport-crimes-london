
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots
#pio.templates.default = "plotly_dark"
import pandas as pd

pio.templates["myWatermark"] = go.layout.Template(layout_annotations=[
    dict(name="watermark",
        text="Dev Anbarasu",
        #textangle=-30,
        opacity=0.1,
        font=dict(color="white", size=25),
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        showarrow=False)
])

pio.templates.default = "plotly_dark+myWatermark"


class SubplotSpecs:
    """
    Represents subplot specifications using a Pandas Series.

    This class stores subplot specifications as a Pandas Series, allowing for 
    easy manipulation and access to individual subplot details.

    Args:
        array (list or pandas.Series): A list or pandas Series containing the 
                                        subplot specifications.  The exact 
                                        interpretation of the data within this 
                                        array is dependent on how it's used 
                                        elsewhere in the code (e.g., it might 
                                        represent row/column indices, titles, etc.).

    Attributes:
        array (pandas.Series): A Pandas Series containing the subplot specifications.
    """
    def __init__(self, array):
        self.array=pd.Series(array)
        
    def get_n_unique(self):
        """Returns the number of unique elements in the array.

        This method leverages the NumPy `nunique()` function to efficiently 
        determine the count of distinct values within the internal array 
        associated with the object.

        Returns:
            int: The number of unique elements in the array.  Returns 0 if the array is empty.
        """
        return self.array.nunique()
    
    def get_n_rows_columns(self,n=False):
        """Determines the optimal number of rows and columns for a grid-like display.

        This function calculates the number of rows and columns needed to display 
        `n` items in a grid, aiming for a roughly square arrangement with at most 
        3 columns.  If `n` is not provided, it defaults to using the result of 
        `self.get_n_unique()`.

        Args:
            n: (optional) The total number of items to be displayed. If False, the 
            number of unique items is obtained using `self.get_n_unique()`.

        Returns:
            A tuple (n_rows, n_cols) containing the calculated number of rows and 
            columns.  The number of columns will be at most 3. The number of rows is 
            calculated to accommodate all items, even if it means having one row with 
            fewer items than others.
        """
        if not n:
            n = self.get_n_unique()
        n_cols = min(3, n)
        #n_rows = (nRaces - n_cols) 
        n_rows=round(n/n_cols)
        if n_rows * n_cols < n:
            n_rows = n_rows + 1
        return n_rows,n_cols

    def get_subplot_matrices(self):
        """Generates dictionaries mapping unique identifiers to subplot row and column counts.

        This function iterates through a sequence of unique identifiers (obtained via `self.get_n_unique()`)
        and determines the optimal number of rows and columns for subplots corresponding to each identifier.
        The results are returned as two dictionaries: one mapping identifiers to row counts and another mapping 
        identifiers to column counts.  Note that the column counts are currently hardcoded to a repeating sequence 
        of [1, 2, 3], regardless of the actual subplot needs determined by `self.get_n_rows_columns()`.  This may need 
        to be adjusted depending on the desired subplot layout.


        Returns:
            tuple: A tuple containing two dictionaries:
                - rows: A dictionary where keys are unique identifiers (integers from 1 to n) and values are the 
                        corresponding number of subplot rows.
                - cols: A dictionary where keys are unique identifiers (integers from 1 to n) and values are the 
                        corresponding number of subplot columns (currently a repeating sequence of [1,2,3]).

        """
        n = self.get_n_unique()
        rows, cols = [], []
        for a in range(1,n+1,1):
            x=a
            n_rows, n_cols = self.get_n_rows_columns(x)
            rows.append(n_rows)
            cols.append(n_cols)


        rows={x:y for x,y in (zip(range(1,n+1),rows))}
        cols={x:y for x,y in (zip(range(1,n+1),[1,2,3]*(n)))}
        return rows, cols
    
    
    def get_subplot_specs(self, d={"type" : "pie"}):
        """Generates a list of specifications based on the number of rows and columns.

        This function calculates the total number of elements based on the number of rows and columns 
        of an object (presumably a grid or matrix represented by the self object). It then creates a 
        list of dictionaries, where each dictionary is a copy of the input dictionary `d`, and the 
        list is structured in groups of three.

        Args:
            d: A dictionary containing specifications (default is {"type": "pie"}).  This dictionary
            is copied and repeated for each element.

        Returns:
            A list of lists, where each inner list contains three dictionaries (copies of `d`).  The 
            number of inner lists is determined by the total number of elements (rows * columns) 
            divided by 3.  If the total number of elements is not divisible by 3, the last inner list 
            will contain fewer than three dictionaries.  Returns an empty list if rows or columns are 0.


        Example:
            If self.get_n_rows_columns() returns (3, 2), meaning 3 rows and 2 columns, then the function
            will return a list containing 2 inner lists, each containing three dictionaries identical
            to the input dictionary `d`.

        """
        #n = self.get_n_unique()
        n_rows, n_cols = self.get_n_rows_columns()
        n = n_rows * n_cols
        specs=list(d.copy() for x in range(n))
        
        specs=[specs[x:x+3] for x in range(0, n, 3)]
        return specs

categorical_color_combinations={
    "twoVariables" : [
        ["MidnightBlue", "LightSkyBlue"],
        ["IndianRed", "LightSalmon"],
        ["Aquamarine", "LightSeaGreen"],
        ["RebeccaPurple", "MediumPurple"],
        ["Orange", "Gold"],
        ["LightSlateGray", "LightSteelBlue"],
        ["DarkBlue", "LightPink"],
        ["Crimson", "PaleTorquoise"]],
    "threeVariables" : [
        ["DarkBlue", "RoyalBlue", "Cyan"],
        ["LightSalmon", "PaleTurquoise", "LightCyan"],
        ["Gold", "MediumTurquoise", "LightGreen"],
        ["MediumSlateBlue", "Lavender", "DarkOrange"]
    ]
}


named_css_colors="aliceblue,antiquewhite,aqua,aquamarine,azure,beige,bisque,black,blanchedalmond,blue,blueviolet,brown,burlywood,cadetblue,chartreuse,chocolate,coral,cornflowerblue,cornsilk,crimson,cyan,darkblue,darkcyan,darkgoldenrod,darkgray,darkgrey,darkgreen,darkkhaki,darkmagenta,darkolivegreen,darkorange,darkorchid,darkred,darksalmon,darkseagreen,darkslateblue,darkslategray,darkslategrey,darkturquoise,darkviolet,deeppink,deepskyblue,dimgray,dimgrey,dodgerblue,firebrick,floralwhite,forestgreen,fuchsia,gainsboro,ghostwhite,gold,goldenrod,gray,grey,green,greenyellow,honeydew,hotpink,indianred,indigo,ivory,khaki,lavender,lavenderblush,lawngreen,lemonchiffon,lightblue,lightcoral,lightcyan,lightgoldenrodyellow,lightgray,lightgrey,lightgreen,lightpink,lightsalmon,lightseagreen,lightskyblue,lightslategray,lightslategrey,lightsteelblue,lightyellow,lime,limegreen,linen,magenta,maroon,mediumaquamarine,mediumblue,mediumorchid,mediumpurple,mediumseagreen,mediumslateblue,mediumspringgreen,mediumturquoise,mediumvioletred,midnightblue,mintcream,mistyrose,moccasin,navajowhite,navy,oldlace,olive,olivedrab,orange,orangered,orchid,palegoldenrod,palegreen,paleturquoise,palevioletred,papayawhip,peachpuff,peru,pink,plum,powderblue,purple,red,rosybrown,royalblue,rebeccapurple,saddlebrown,salmon,sandybrown,seagreen,seashell,sienna,silver,skyblue,slateblue,slategray,slategrey,snow,springgreen,steelblue,tan,teal,thistle,tomato,turquoise,violet,wheat,white,whitesmoke,yellow,yellowgreen"

named_css_colors=named_css_colors.split(",")
