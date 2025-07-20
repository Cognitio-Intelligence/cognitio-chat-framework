/// <reference types="node" />

declare namespace NodeJS {
  interface ProcessEnv {
    readonly NODE_ENV: 'development' | 'production' | 'test'
    readonly CLOUD_API_URL?: string
    // add more env variables here as needed
  }
}

declare var process: {
  env: NodeJS.ProcessEnv
} 