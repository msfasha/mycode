#!/usr/bin/env python3
"""
Network Visualizer for EPANET Simulations
=========================================

A comprehensive visualization module for EPANET networks using EPyT.
This module provides various plotting functions that can be used across
different simulation scripts.

Usage:
    from network_visualizer import plot_comprehensive_network
    plot_comprehensive_network(d)
"""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for web app
import matplotlib.pyplot as plt
import numpy as np
from epyt import epanet

def plot_network_topology(d, title="EPANET Network Topology", save_path=None):
    """
    Plot basic network topology with nodes and links
    
    Args:
        d: EPANET network object
        title: Plot title
        save_path: Optional path to save the plot
    """
    try:
        plt.figure(figsize=(12, 8))
        d.plot()
        plt.title(title, fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        
        if save_path:
            if hasattr(save_path, 'write'):  # It's a file-like object
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
            else:  # It's a file path
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                print(f"Network topology plot saved to: {save_path}")
        else:
            plt.show()
        
    except Exception as e:
        print(f"Error plotting network topology: {e}")

def plot_pressure_distribution(d, title="Pressure Distribution", save_path=None):
    """
    Plot nodes colored by pressure levels
    
    Args:
        d: EPANET network object
        title: Plot title
        save_path: Optional path to save the plot
    """
    try:
        plt.figure(figsize=(12, 8))
        d.plot(parameter='pressure')
        plt.title(title, fontsize=14, fontweight='bold')
        plt.colorbar(label='Pressure (m)')
        plt.grid(True, alpha=0.3)
        
        if save_path:
            if hasattr(save_path, 'write'):  # It's a file-like object
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
            else:  # It's a file path
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                print(f"Pressure distribution plot saved to: {save_path}")
        else:
            plt.show()
        
    except Exception as e:
        print(f"Error plotting pressure distribution: {e}")

def plot_flow_patterns(d, title="Flow Patterns", save_path=None):
    """
    Plot links with flow directions and magnitudes
    
    Args:
        d: EPANET network object
        title: Plot title
        save_path: Optional path to save the plot
    """
    try:
        plt.figure(figsize=(12, 8))
        d.plot(parameter='flow')
        plt.title(title, fontsize=14, fontweight='bold')
        plt.colorbar(label='Flow (L/s)')
        plt.grid(True, alpha=0.3)
        
        if save_path:
            if hasattr(save_path, 'write'):  # It's a file-like object
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
            else:  # It's a file path
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                print(f"Flow patterns plot saved to: {save_path}")
        else:
            plt.show()
        
    except Exception as e:
        print(f"Error plotting flow patterns: {e}")

def plot_comprehensive_network(d, show_pressure=True, show_flow=True, 
                              title="Comprehensive Network Analysis", save_path=None):
    """
    Create a comprehensive network visualization with multiple subplots
    
    Args:
        d: EPANET network object
        show_pressure: Whether to show pressure distribution
        show_flow: Whether to show flow patterns
        title: Main title for the plot
        save_path: Optional path to save the plot
    """
    try:
        # Determine number of subplots
        num_plots = 1  # Always show topology
        if show_pressure:
            num_plots += 1
        if show_flow:
            num_plots += 1
        
        # Create subplots
        fig, axes = plt.subplots(1, num_plots, figsize=(6*num_plots, 8))
        if num_plots == 1:
            axes = [axes]
        
        plot_idx = 0
        
        # Plot 1: Network Topology
        axes[plot_idx].set_title("Network Topology", fontweight='bold')
        d.plot(ax=axes[plot_idx])
        axes[plot_idx].grid(True, alpha=0.3)
        plot_idx += 1
        
        # Plot 2: Pressure Distribution (if requested)
        if show_pressure:
            axes[plot_idx].set_title("Pressure Distribution", fontweight='bold')
            d.plot(parameter='pressure', ax=axes[plot_idx])
            axes[plot_idx].grid(True, alpha=0.3)
            plot_idx += 1
        
        # Plot 3: Flow Patterns (if requested)
        if show_flow:
            axes[plot_idx].set_title("Flow Patterns", fontweight='bold')
            d.plot(parameter='flow', ax=axes[plot_idx])
            axes[plot_idx].grid(True, alpha=0.3)
        
        plt.suptitle(title, fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        if save_path:
            if hasattr(save_path, 'write'):  # It's a file-like object
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
            else:  # It's a file path
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                print(f"Comprehensive network plot saved to: {save_path}")
        else:
            plt.show()
        
    except Exception as e:
        print(f"Error creating comprehensive network plot: {e}")

def plot_network_statistics(d, title="Network Statistics", save_path=None):
    """
    Plot network statistics and summary information
    
    Args:
        d: EPANET network object
        title: Plot title
        save_path: Optional path to save the plot
    """
    try:
        # Get network statistics
        node_count = d.getNodeCount()
        link_count = d.getLinkCount()
        junction_count = d.getNodeJunctionCount()
        tank_count = d.getNodeTankCount()
        
        # Get current pressures and flows
        pressures = d.getNodePressure()
        flows = d.getLinkFlows()
        
        # Create statistics plot
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
        
        # Network composition
        categories = ['Junctions', 'Tanks', 'Links']
        counts = [junction_count, tank_count, link_count]
        colors = ['skyblue', 'lightcoral', 'lightgreen']
        
        ax1.pie(counts, labels=categories, colors=colors, autopct='%1.0f')
        ax1.set_title('Network Composition')
        
        # Pressure distribution histogram
        ax2.hist(pressures, bins=20, alpha=0.7, color='blue', edgecolor='black')
        ax2.set_xlabel('Pressure (m)')
        ax2.set_ylabel('Frequency')
        ax2.set_title('Pressure Distribution')
        ax2.grid(True, alpha=0.3)
        
        # Flow distribution histogram
        ax3.hist(np.abs(flows), bins=20, alpha=0.7, color='green', edgecolor='black')
        ax3.set_xlabel('Flow Magnitude (L/s)')
        ax3.set_ylabel('Frequency')
        ax3.set_title('Flow Distribution')
        ax3.grid(True, alpha=0.3)
        
        # Summary statistics
        ax4.axis('off')
        stats_text = f"""
        Network Summary:
        • Total Nodes: {node_count}
        • Junctions: {junction_count}
        • Tanks: {tank_count}
        • Links: {link_count}
        
        Current State:
        • Avg Pressure: {np.mean(pressures):.2f} m
        • Min Pressure: {np.min(pressures):.2f} m
        • Max Pressure: {np.max(pressures):.2f} m
        • Total Flow: {np.sum(np.abs(flows)):.2f} L/s
        """
        ax4.text(0.1, 0.9, stats_text, transform=ax4.transAxes, 
                fontsize=10, verticalalignment='top', fontfamily='monospace')
        
        plt.suptitle(title, fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        if save_path:
            if hasattr(save_path, 'write'):  # It's a file-like object
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
            else:  # It's a file path
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                print(f"Network statistics plot saved to: {save_path}")
        else:
            plt.show()
        
    except Exception as e:
        print(f"Error plotting network statistics: {e}")

def save_network_plot(d, filename, plot_type="comprehensive"):
    """
    Save network plot to file with specified type
    
    Args:
        d: EPANET network object
        filename: Output filename
        plot_type: Type of plot ('topology', 'pressure', 'flow', 'comprehensive', 'statistics')
    """
    try:
        if plot_type == "topology":
            plot_network_topology(d, save_path=filename)
        elif plot_type == "pressure":
            plot_pressure_distribution(d, save_path=filename)
        elif plot_type == "flow":
            plot_flow_patterns(d, save_path=filename)
        elif plot_type == "comprehensive":
            plot_comprehensive_network(d, save_path=filename)
        elif plot_type == "statistics":
            plot_network_statistics(d, save_path=filename)
        else:
            print(f"Unknown plot type: {plot_type}")
            print("Available types: 'topology', 'pressure', 'flow', 'comprehensive', 'statistics'")
            return False
        
        print(f"Network plot saved successfully to: {filename}")
        return True
            
    except Exception as e:
        print(f"Error saving network plot: {e}")
        return False

def visualize_network_interactive(d, title="Interactive Network Visualization"):
    """
    Create an interactive network visualization (if supported)
    
    Args:
        d: EPANET network object
        title: Plot title
    """
    try:
        print("Creating interactive network visualization...")
        
        # Basic interactive plot
        plt.figure(figsize=(14, 10))
        d.plot()
        plt.title(title, fontsize=16, fontweight='bold')
        plt.grid(True, alpha=0.3)
        
        # Add interactive elements
        plt.xlabel('X Coordinate', fontsize=12)
        plt.ylabel('Y Coordinate', fontsize=12)
        
        # Add legend
        plt.legend(['Nodes', 'Links'], loc='upper right')
        
        plt.show()
        
    except Exception as e:
        print(f"Error creating interactive visualization: {e}")

# Example usage function
def demo_visualization(network_file):
    """
    Demonstrate all visualization capabilities
    
    Args:
        network_file: Path to EPANET .inp file
    """
    try:
        print("Loading network for visualization demo...")
        d = epanet(network_file)
        
        print("\n1. Network Topology")
        plot_network_topology(d)
        
        print("\n2. Pressure Distribution")
        plot_pressure_distribution(d)
        
        print("\n3. Flow Patterns")
        plot_flow_patterns(d)
        
        print("\n4. Comprehensive Analysis")
        plot_comprehensive_network(d)
        
        print("\n5. Network Statistics")
        plot_network_statistics(d)
        
        d.unload()
        print("\nVisualization demo completed!")
        
    except Exception as e:
        print(f"Error in visualization demo: {e}")

if __name__ == "__main__":
    # Demo the visualizer
    demo_visualization("water-networks/Net1.inp")
