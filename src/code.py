import sys
sys.path.append('src')
from splash_screen import SplashScreen

# Show splash screen and display while other stuff loads
splash_screen = SplashScreen()
splash_screen.show()

# Import and start colorimeter
from colorimeter import Colorimeter 
colorimeter = Colorimeter()
colorimeter.run()

