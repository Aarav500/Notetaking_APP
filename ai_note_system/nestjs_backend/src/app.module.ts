import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { ConfigModule, ConfigService } from '@nestjs/config';
import { User } from './entities/user.entity';
import { Note } from './entities/note.entity';
import { Flowchart } from './entities/flowchart.entity';
import { UsersModule } from './users/users.module';
import { AuthModule } from './auth/auth.module';
import { NotesModule } from './notes/notes.module';
import { FlowchartsModule } from './flowcharts/flowcharts.module';
import { AiModule } from './ai/ai.module';

@Module({
  imports: [
    // Load environment variables
    ConfigModule.forRoot({
      isGlobal: true,
    }),

    // Configure TypeORM with environment switching (sqlite default for dev)
    TypeOrmModule.forRootAsync({
      imports: [ConfigModule],
      inject: [ConfigService],
      useFactory: (config: ConfigService) => {
        const dbType = (config.get<string>('DB_TYPE') || 'sqlite').toLowerCase();
        const synchronize = (config.get<string>('DB_SYNCHRONIZE') || 'true') === 'true';

        if (dbType === 'oracle') {
          return {
            type: 'oracle' as const,
            host: config.get<string>('DB_HOST', 'localhost'),
            port: config.get<number>('DB_PORT', 1521),
            username: config.get<string>('DB_USERNAME', 'admin'),
            password: config.get<string>('DB_PASSWORD', 'password'),
            sid: config.get<string>('DB_SID', 'ORCLCDB'),
            autoLoadEntities: true,
            synchronize,
          };
        }

        if (dbType === 'postgres' || dbType === 'postgresql' || dbType === 'pg') {
          return {
            type: 'postgres' as const,
            host: config.get<string>('DB_HOST', 'localhost'),
            port: config.get<number>('DB_PORT', 5432),
            username: config.get<string>('DB_USERNAME', 'postgres'),
            password: config.get<string>('DB_PASSWORD', 'postgres'),
            database: config.get<string>('DB_NAME', 'ai_notes'),
            autoLoadEntities: true,
            synchronize,
          };
        }

        // default: sqlite for local dev
        return {
          type: 'sqlite' as const,
          database: config.get<string>('SQLITE_DB', 'dev.sqlite'),
          autoLoadEntities: true,
          synchronize,
        };
      },
    }),

    // Feature modules will be added here (Auth, Users, Notes, Flowcharts, AI)
    UsersModule,
    AuthModule,
    NotesModule,
    FlowchartsModule,
    AiModule,
  ],
  controllers: [],
  providers: [],
})
export class AppModule {}