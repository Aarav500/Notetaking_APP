import { Entity, PrimaryGeneratedColumn, Column, ManyToOne, JoinColumn } from 'typeorm';
import { User } from './user.entity';

@Entity('flowcharts')
export class Flowchart {
  @PrimaryGeneratedColumn()
  id: number;

  @Column()
  title: string;

  // Use portable text type for cross-DB compatibility
  @Column({ type: 'text' })
  nodes: string; // Store serialized nodes

  @Column({ type: 'text' })
  edges: string; // Store serialized edges

  @ManyToOne(() => User, user => user.flowcharts)
  @JoinColumn({ name: 'user_id' })
  user: User;
}