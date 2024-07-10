import numpy as np

np.random.seed(12345)


def generar_instancia(I, J, N=4):
    # Niveles de especialización (distribución triangular)
    E = np.random.triangular(1, 8, 8, I).astype(int)
    S = np.random.triangular(1, 1, 8, J).astype(int)

    # Tiempo disponible por trabajador y tiempo requerido por tarea
    inf_limit = 20 + 10*N
    sup_limit = inf_limit + 15
    H = np.random.randint(inf_limit, sup_limit, I)*10
    T = np.random.randint(3, inf_limit, J)*10

    # Costos por unidad de tiempo por trabajador
    costo_tiempo = lambda n_e: np.random.uniform(5*n_e, 5*n_e+5)
    U = costo_tiempo(E)

    # Costos fijos y costos de sobrecalificación
    C = np.random.randint(4000, 8001, size=(I, J))
    O = np.random.randint(10000, 30001, size=(J))

    # Presupuesto
    P = (np.random.randint(low=(20000)//3, high=(40000)//5, size=1)*I)[0]

    return E.tolist(), S.tolist(), H.tolist(), T.tolist(), U.tolist(), C.tolist(), O.tolist(), P, N, I, J


def MiniZinc_text(E:list,S:list,H:list,T:list,U:list,C:list,O:list,P:float,I:int,J:int,N:int):

    def list2d_to_minizinc2dstring(elements: list):
        result = "["
        for line in elements:
            result += "|"+str(line)[1:-1]
        result += "|]"
        return(result)
    
    list_of_lines = []
    #Sets
    list_of_lines.append(f"int: I = {I};")
    list_of_lines.append(f"int: J = {J};")
    list_of_lines.append(f"set of int: empleados = 1..I;")
    list_of_lines.append(f"set of int: tareas = 1..J;")
    list_of_lines.append(f"array[1..I] of float: E = {E};")
    list_of_lines.append(f"array[1..J] of float: S = {S};")
    list_of_lines.append(f"array[1..J] of float: T = {T};")
    list_of_lines.append(f"array[1..I] of float: H = {H};")
    list_of_lines.append(f"array[empleados,tareas] of float: C = {list2d_to_minizinc2dstring(C)};")
    list_of_lines.append(f"array[1..I] of float: U = {U};")
    list_of_lines.append(f"array[tareas] of float: O = {O};")
    list_of_lines.append(f"int: P = {P};")
    list_of_lines.append(f"int: N={N};")

    #Variables
    list_of_lines.append(f"array[empleados,tareas] of var 0..1: x;")
    list_of_lines.append(f"array[empleados,tareas] of var float: y;")

    #func. objetivo
    list_of_lines.append(f"var float: funcob = sum ([ sum ([ C[i,j]*x[i,j] + U[i]*y[i,j] | j in 1..J]) | i in 1..I]);")

    #restricciones
    list_of_lines.append(f"constraint forall(j in 1..J)(sum([ y[i,j] | i in 1..I]) >= T[j]);")
    list_of_lines.append(f"constraint forall(i in 1..I)(sum([y[i,j] | j in 1..J ]) <= H[i]);")
    list_of_lines.append(f"constraint forall(i in 1..I)(forall(j in 1..J) ( x[i,j]*E[i] - x[i,j]*S[j] >= 0));")
    list_of_lines.append(f"constraint forall(i in 1..I)(forall(j in 1..J)( y[i,j] <= T[j]*x[i,j] ));")
    list_of_lines.append(f"constraint forall(i in 1..I)( sum([ x[i,j] | j in 1..J]) <= N );")
    list_of_lines.append(f"constraint  sum ([ sum ([ C[i,j]*x[i,j] + U[i]*y[i,j] + bool2int(E[i]>S[j])*O[j]*x[i,j]| j in 1..J]) | i in 1..I]) <= P;")
    list_of_lines.append(f"constraint forall(j in 1..J)( sum([ x[i,j] | i in 1..I]) <= 2 * I / 3 );")

    #solve
    list_of_lines.append("solve minimize funcob;")
    list_of_lines.append("output [\"xij = \\(x)\\n\", \"yij = \\(y)\\n\", \"costos = \\(funcob)\"]")

    return list_of_lines
#funcion generadora
range_func = lambda left_limit, distance: np.random.randint(left_limit, left_limit+distance)


#instancias pequenas
I_pequena_i = np.arange(1,6)*10
I_pequena = range_func(I_pequena_i, 9)
J_pequena = np.random.randint(np.array([5,8,13,19,24]), np.array([7,12,18,23,30]))

#instancias medianas
I_mediana_i = np.arange(80,205,25)
I_mediana = range_func(I_mediana_i, 24)
J_mediana_i = np.arange(30,105,15)
J_mediana = range_func(J_mediana_i, 14) 

#instancias grandes
I_grande_i = np.arange(300,600,60)
I_grande = range_func(I_grande_i, 59)
J_grande_i = np.arange(100,300,40)
J_grande = range_func(J_grande_i, 39)

I = np.concatenate((I_pequena,I_mediana,I_grande))
J = np.concatenate((J_pequena,J_mediana,J_grande))

#instancias
instancias = []
for i in range(len(I)):
    instancias.append(generar_instancia(I[i], J[i]))

i = 1
for E, S, H, T, U, C, O, P, N, I, J in instancias:
    file = open(f'instancia-{i}.mzn', 'w')
    for line in MiniZinc_text(E=E, S=S, H=H, T=T, U=U, C=C, O=O, P=P, I=I, J=J, N=N):
        file.write(line+"\n")
    file.close()
    i+= 1