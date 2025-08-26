# AI Note System - NestJS Backend

This is the NestJS backend for the AI Note System, configured to work with an Oracle database.

## Local Development Setup

### Prerequisites

- Node.js and npm
- Oracle Instant Client (required for the oracledb package)
- Oracle database (or you can use SQLite/PostgreSQL locally and switch configs when deploying)

### Installation

1. Install dependencies:

```bash
npm install
```

2. Configure environment variables:

Copy the `.env.example` file to `.env` and update the values as needed:

```
# Database Configuration
DB_TYPE=oracle
DB_HOST=localhost
DB_PORT=1521
DB_USERNAME=admin
DB_PASSWORD=password
DB_SID=ORCLCDB
DB_SYNCHRONIZE=true

# Application Configuration
PORT=3000
NODE_ENV=development
```

For local development, you can use SQLite or PostgreSQL instead of Oracle by changing the DB_TYPE and related configuration.

### Running the Application

```bash
# Development mode
npm run start:dev

# Production mode
npm run start:prod
```

## Database Schema

The application uses TypeORM with the following entities:

### User Entity

```typescript
@Entity('users')
export class User {
  @PrimaryGeneratedColumn()
  id: number;

  @Column({ unique: true })
  email: string;

  @Column()
  password: string;

  @OneToMany(() => Note, note => note.user)
  notes: Note[];
  
  @OneToMany(() => Flowchart, flowchart => flowchart.user)
  flowcharts: Flowchart[];
}
```

### Note Entity

```typescript
@Entity('notes')
export class Note {
  @PrimaryGeneratedColumn()
  id: number;

  @Column()
  title: string;

  @Column('clob')
  content: string; // Use CLOB for large text

  @Column({ default: false })
  is_ai_generated: boolean;

  @ManyToOne(() => User, user => user.notes)
  @JoinColumn({ name: 'user_id' })
  user: User;
}
```

### Flowchart Entity

```typescript
@Entity('flowcharts')
export class Flowchart {
  @PrimaryGeneratedColumn()
  id: number;

  @Column()
  title: string;

  @Column('clob')
  nodes: string; // Store serialized nodes

  @Column('clob')
  edges: string; // Store serialized edges

  @ManyToOne(() => User, user => user.flowcharts)
  @JoinColumn({ name: 'user_id' })
  user: User;
}
```

## Next Steps

- [ ] Add CRUD endpoints for notes & flowcharts
- [ ] Add guards for @UseGuards(AuthGuard) on private routes
- [ ] Setup service layer (e.g., note.service.ts)
- [ ] Test all endpoints with sample user

## Oracle Database Notes

For the oracledb package to work locally, you'll need Oracle Instant Client installed. You can download it from the Oracle website.

For production deployment, you'll need to update the database configuration to point to your Oracle ATP instance.