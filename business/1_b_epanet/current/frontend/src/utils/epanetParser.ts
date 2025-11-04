export interface Junction {
  id: string;
  elevation: number;
  demand: number;
  pattern?: string;
}

export interface Reservoir {
  id: string;
  head: number;
  pattern?: string;
}

export interface Tank {
  id: string;
  elevation: number;
  initLevel: number;
  minLevel: number;
  maxLevel: number;
  diameter: number;
  minVol: number;
  volCurve?: string;
}

export interface Pipe {
  id: string;
  node1: string;
  node2: string;
  length: number;
  diameter: number;
  roughness: number;
  minorLoss: number;
  status: string;
}

export interface Pump {
  id: string;
  node1: string;
  node2: string;
  parameters: string;
}

export interface Valve {
  id: string;
  node1: string;
  node2: string;
  diameter: number;
  type: string;
  setting: number;
  minorLoss: number;
}

export interface Coordinate {
  nodeId: string;
  x: number;
  y: number;
}

export interface ParsedNetwork {
  title: string;
  junctions: Junction[];
  reservoirs: Reservoir[];
  tanks: Tank[];
  pipes: Pipe[];
  pumps: Pump[];
  valves: Valve[];
  coordinates: Coordinate[];
  demands: Array<{
    junction: string;
    demand: number;
    pattern?: string;
    category?: string;
  }>;
}

export class EPANETParser {
  private parseSection(sectionName: string, lines: string[]): string[] {
    const startIndex = lines.findIndex(line => 
      line.trim().toUpperCase() === `[${sectionName.toUpperCase()}]`
    );
    
    if (startIndex === -1) return [];
    
    const sectionLines: string[] = [];
    for (let i = startIndex + 1; i < lines.length; i++) {
      const line = lines[i].trim();
      
      // Stop at next section or empty line
      if (line.startsWith('[') || line === '') {
        break;
      }
      
      // Skip comment lines
      if (line.startsWith(';') || line === '') {
        continue;
      }
      
      sectionLines.push(line);
    }
    
    return sectionLines;
  }

  private parseJunctions(lines: string[]): Junction[] {
    const sectionLines = this.parseSection('JUNCTIONS', lines);
    return sectionLines.map(line => {
      const parts = line.split(/\s+/).filter(part => part !== '');
      return {
        id: parts[0],
        elevation: parseFloat(parts[1]) || 0,
        demand: parseFloat(parts[2]) || 0,
        pattern: parts[3] || undefined
      };
    });
  }

  private parseReservoirs(lines: string[]): Reservoir[] {
    const sectionLines = this.parseSection('RESERVOIRS', lines);
    return sectionLines.map(line => {
      const parts = line.split(/\s+/).filter(part => part !== '');
      return {
        id: parts[0],
        head: parseFloat(parts[1]) || 0,
        pattern: parts[2] || undefined
      };
    });
  }

  private parseTanks(lines: string[]): Tank[] {
    const sectionLines = this.parseSection('TANKS', lines);
    return sectionLines.map(line => {
      const parts = line.split(/\s+/).filter(part => part !== '');
      return {
        id: parts[0],
        elevation: parseFloat(parts[1]) || 0,
        initLevel: parseFloat(parts[2]) || 0,
        minLevel: parseFloat(parts[3]) || 0,
        maxLevel: parseFloat(parts[4]) || 0,
        diameter: parseFloat(parts[5]) || 0,
        minVol: parseFloat(parts[6]) || 0,
        volCurve: parts[7] || undefined
      };
    });
  }

  private parsePipes(lines: string[]): Pipe[] {
    const sectionLines = this.parseSection('PIPES', lines);
    return sectionLines.map(line => {
      const parts = line.split(/\s+/).filter(part => part !== '');
      return {
        id: parts[0],
        node1: parts[1],
        node2: parts[2],
        length: parseFloat(parts[3]) || 0,
        diameter: parseFloat(parts[4]) || 0,
        roughness: parseFloat(parts[5]) || 0,
        minorLoss: parseFloat(parts[6]) || 0,
        status: parts[7] || 'Open'
      };
    });
  }

  private parsePumps(lines: string[]): Pump[] {
    const sectionLines = this.parseSection('PUMPS', lines);
    return sectionLines.map(line => {
      const parts = line.split(/\s+/).filter(part => part !== '');
      return {
        id: parts[0],
        node1: parts[1],
        node2: parts[2],
        parameters: parts.slice(3).join(' ')
      };
    });
  }

  private parseValves(lines: string[]): Valve[] {
    const sectionLines = this.parseSection('VALVES', lines);
    return sectionLines.map(line => {
      const parts = line.split(/\s+/).filter(part => part !== '');
      return {
        id: parts[0],
        node1: parts[1],
        node2: parts[2],
        diameter: parseFloat(parts[3]) || 0,
        type: parts[4] || '',
        setting: parseFloat(parts[5]) || 0,
        minorLoss: parseFloat(parts[6]) || 0
      };
    });
  }

  private parseCoordinates(lines: string[]): Coordinate[] {
    const sectionLines = this.parseSection('COORDINATES', lines);
    return sectionLines.map(line => {
      const parts = line.split(/\s+/).filter(part => part !== '');
      return {
        nodeId: parts[0],
        x: parseFloat(parts[1]) || 0,
        y: parseFloat(parts[2]) || 0
      };
    });
  }

  private parseDemands(lines: string[]): Array<{
    junction: string;
    demand: number;
    pattern?: string;
    category?: string;
  }> {
    const sectionLines = this.parseSection('DEMANDS', lines);
    return sectionLines.map(line => {
      const parts = line.split(/\s+/).filter(part => part !== '');
      return {
        junction: parts[0],
        demand: parseFloat(parts[1]) || 0,
        pattern: parts[2] || undefined,
        category: parts[3] || undefined
      };
    });
  }

  private parseTitle(lines: string[]): string {
    const titleSection = this.parseSection('TITLE', lines);
    return titleSection.join(' ').trim() || 'Untitled Network';
  }

  public parseINPFile(content: string): ParsedNetwork {
    const lines = content.split('\n');
    
    return {
      title: this.parseTitle(lines),
      junctions: this.parseJunctions(lines),
      reservoirs: this.parseReservoirs(lines),
      tanks: this.parseTanks(lines),
      pipes: this.parsePipes(lines),
      pumps: this.parsePumps(lines),
      valves: this.parseValves(lines),
      coordinates: this.parseCoordinates(lines),
      demands: this.parseDemands(lines)
    };
  }

  public async parseINPFileFromFile(file: File): Promise<ParsedNetwork> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      
      reader.onload = (e) => {
        try {
          const content = e.target?.result as string;
          const parsed = this.parseINPFile(content);
          resolve(parsed);
        } catch (error) {
          reject(new Error(`Failed to parse INP file: ${error}`));
        }
      };
      
      reader.onerror = () => {
        reject(new Error('Failed to read file'));
      };
      
      reader.readAsText(file);
    });
  }
}

// Export a default instance
export const epanetParser = new EPANETParser();
