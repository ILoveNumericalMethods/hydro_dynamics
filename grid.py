import numpy
import Vector
import mapping

e_vectors = numpy.array([Vector(0, 0), Vector(0, 1), Vector(1, 1), Vector(1, 0), Vector(1, -1), Vector(0, -1), Vector(-1, -1), Vector(-1, 0), Vector(-1, 1)])

standart_coefficient_array = numpy.array([1 / 36, 1 / 18, 1 / 36],
                                         [1 / 18, 1 / 3, 1 / 18],
                                         [1 / 36, 1 / 18, 1 / 36])


class Node:
    """    
    узел расчетной ячейки    
    направления нумерются с центрального, далее верхний и по часовой стреке    
    macro_velocity - вектор скорости   
    micro_velocity_array - массив скоростей по направлениям - строка
    coefficient_array - коэффициенты напрвлений - диагональная матрица    
    Boltzmann_function -  функцией распределения плотности вероятности частиц по координатам и по скоростям - столбец    
    distribution_function - равновесная функция распределения - столбец    
    density - плотность жидкости    
    """   
    
    def __init__ (self, macro_velocity, micro_velocity_array, coefficient_array, Boltzmann_function, distribution_function, density):
        """        
        Конструктор        
        """        
        self.macro_velocity = macro_velocity
        self.micro_velocity_array = micro_velocity_array
        self.coefficient_array = coefficient_array
        self.Boltzmann_function = Boltzmann_function
        self.distribution_function = distribution_function
        self.density = density

    def calculate_Boltzmann_function_around (self, tau):
        """        
        расчитаывает приращения функций Больтсмана для каждой частицы вокруг данной        
        """       
        return -1 * (self.Boltzmann_function - self.distribution_function) / tau

    def calculate_density (self):
        """        
        считает плотность        
        """        
        self.density = numpy.sum(self.Boltzmann_function)

    def calculate_macro_velocity (self):
        """        
        считает скорость        
        """        
        self.macro_velocity += self.micro_velocity_array * self.Boltzmann_function

        self.micro_velocity_array /= self.density

    def calculate_distribution_function (self, R, T):
        """        
        расчитаывает функцию по направлению        
        """        
        self.distribution_function = numpy.array([0, 1, 2, 3, 4, 5, 6, 7, 8])

        self.distribution_function = (1 + (e_vectors[self.distribution_function] * self.macro_velocity) / (R * T)
                                      + (e_vectors[self.distribution_function] * self.macro_velocity) ** 2 / (2 * (R * T) ** 2)
                                      - self.macro_velocity * self.macro_velocity / (2 * R * T))

        self.distribution_function *= self.density
        self.distribution_function = self.coefficient_array * self.distribution_function

    def calculate_Boltzmann_function_in_this_node (self, tau):
        """        
        расчитаывает функций Больтсмана в узле        
        """        
        self.Boltzmann_function -= (self.Boltzmann_function - self.distribution_function) / tau


class greed:
    """    
    Расчетная сетка    
    object - объект    
    length - длина трубы    
    width - толщина трубы        
    start_velocity - начальная скорость течения    
    grid - сетка    
    density - плотность
    R - универсальчная газовая постоянная
    T - температура
    t - параметр
    """

    def __init__ (self, length, width, object, density, R, T, t):

        grid_map = mapping.made_map(length, width, object)

        self.grid = [[Node(Vector(0, 0), numpy.zeros((1, 9)), standart_coefficient_array, numpy.zeros((9, 1)), numpy.zeros((9, 1)), decity)] * width] * length

        for i in range(length + 2):
            for j in range(width + 2):
                if (grid_map[i][j] == 1):
                    self.grid[i][j].coefficient_array = numpy.zeros((3, 3))
                    self.grid[i][j].coefficient_array = mapping.make_coefficient_array(grid_map, length, width, i , j)
        
        self.object = object
        self.length = length
        self.width = width
        self.density = density
        self.R = R
        self.T = T
        self.t = t

    def modeling(self):
        for j in range(self.width):
            self.grid[1][j + 1].macro_velocity = Vector(0.1, 0)            
            self.grid[1][j + 1].micro_velocity_array = numpy.array([0, 0.1, 0, 0, 0, 0, 0, 0, 0])
            self.grid[1][j + 1].Boltzmann_function = numpy.array([0, 1, 0, 0, 0, 0, 0, 0, 0]).transpose()
            self.grid[1][j + 1].calculate_distribution_function(self.R, self.T)
            self.grid[1][j + 1] = self.density

        for i in range(self.length):
            for j in range(self.width):
                
                delta_f = self.grid[i + 1][j + 1].calculate_Boltzmann_function_around(self.t)
                self.grid[i + 1][j + 1].Boltzmann_function[0][0] = delta_f[0][0]
                self.grid[i + 2][j + 1].Boltzmann_function[1][0] = delta_f[1][0]
                self.grid[i + 2][j + 2].Boltzmann_function[2][0] = delta_f[2][0]
                self.grid[i + 1][j + 2].Boltzmann_function[3][0] = delta_f[3][0]
                self.grid[i][j + 2].Boltzmann_function[4][0] = delta_f[4][0]
                self.grid[i][j + 1].Boltzmann_function[5][0] = delta_f[5][0]
                self.grid[i][j].Boltzmann_function[6][0] = delta_f[6][0]
                self.grid[i + 1][j].Boltzmann_function[7][0] = delta_f[7][0]
                self.grid[i + 2][j].Boltzmann_function[8][0] = delta_f[8][0]
