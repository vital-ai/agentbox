import matplotlib.pyplot as plt
import numpy as np

# Generate sample data: a sine wave
x = np.linspace(0, 10, 500)
y = np.sin(x)

# Create the plot
plt.figure(figsize=(8, 4))
plt.plot(x, y, label='sin(x)', color='blue', linewidth=2)
plt.title('Sample Chart: Sine Wave')
plt.xlabel('X Axis')
plt.ylabel('Y Axis')
plt.legend()
plt.grid(True)

# Save the chart as a PNG file
plt.savefig('chart.png', dpi=300, bbox_inches='tight')
plt.close()

print("Chart saved as 'chart.png'.")
