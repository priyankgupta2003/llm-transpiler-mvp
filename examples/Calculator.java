public class Calculator {
    private double result;
    
    public Calculator() {
        this.result = 0.0;
    }
    
    public double add(double a, double b) {
        result = a + b;
        return result;
    }
    
    public double subtract(double a, double b) {
        result = a - b;
        return result;
    }
    
    public double multiply(double a, double b) {
        result = a * b;
        return result;
    }
    
    public double divide(double a, double b) throws ArithmeticException {
        if (b == 0) {
            throw new ArithmeticException("Cannot divide by zero");
        }
        result = a / b;
        return result;
    }
    
    public double getResult() {
        return result;
    }
    
    public void reset() {
        result = 0.0;
    }
    
    public static void main(String[] args) {
        Calculator calc = new Calculator();
        
        System.out.println("Addition: " + calc.add(10, 5));
        System.out.println("Subtraction: " + calc.subtract(10, 5));
        System.out.println("Multiplication: " + calc.multiply(10, 5));
        
        try {
            System.out.println("Division: " + calc.divide(10, 5));
            System.out.println("Division by zero: " + calc.divide(10, 0));
        } catch (ArithmeticException e) {
            System.out.println("Error: " + e.getMessage());
        }
        
        System.out.println("Final result: " + calc.getResult());
    }
}