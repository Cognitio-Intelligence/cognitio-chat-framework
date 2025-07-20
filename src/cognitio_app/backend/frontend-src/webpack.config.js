const path = require("path");
const webpack = require("webpack");

// Custom plugin to handle node: imports
class NodeProtocolPlugin {
  apply(compiler) {
    compiler.hooks.normalModuleFactory.tap("NodeProtocolPlugin", (factory) => {
      factory.hooks.beforeResolve.tap("NodeProtocolPlugin", (data) => {
        if (data && data.request && data.request.startsWith("node:")) {
          data.request = data.request.replace("node:", "");
        }
      });
    });
  }
}

// Custom plugin to remove empty chunks
class RemoveEmptyChunksPlugin {
  apply(compiler) {
    compiler.hooks.compilation.tap('RemoveEmptyChunksPlugin', (compilation) => {
      compilation.hooks.optimizeChunks.tap('RemoveEmptyChunksPlugin', (chunks) => {
        chunks.forEach((chunk) => {
          if (chunk.name !== 'main' && chunk.isEmpty()) {
            compilation.chunks.delete(chunk);
          }
        });
      });
    });
  }
}

module.exports = {
  entry: "./src/main.tsx",
  output: {
    path: path.resolve(__dirname, "dist"),
    filename: "main.js",
    publicPath: "/static/assets/",
    clean: true, // This ensures old files are removed
    // Prevent asset duplication
    assetModuleFilename: 'assets/[name][ext]'
  },
  mode: process.env.NODE_ENV === 'production' ? 'production' : 'development',
  devtool: process.env.NODE_ENV === 'production' ? 'source-map' : 'eval-source-map',
  module: {
    rules: [
      {
        test: /\.(ts|tsx)$/,
        exclude: /node_modules/,
        use: [
          {
            loader: "babel-loader",
            options: {
              presets: [
                ["@babel/preset-env", {
                  targets: {
                    browsers: ["> 1%", "last 2 versions", "not ie <= 8"]
                  },
                  modules: false,
                  useBuiltIns: "usage",
                  corejs: 3
                }],
                ["@babel/preset-react", {
                  runtime: "automatic"
                }],
                "@babel/preset-typescript"
              ],
              plugins: [
                "@babel/plugin-transform-class-properties",
                "@babel/plugin-transform-object-rest-spread",
                "@babel/plugin-syntax-dynamic-import",
                ["@babel/plugin-transform-runtime", {
                  corejs: false,
                  helpers: true,
                  regenerator: true,
                  useESModules: false
                }],
                ...(process.env.NODE_ENV === 'development' ? ["react-refresh/babel"] : [])
              ],
            },
          },
          {
            loader: "ts-loader",
            options: {
              configFile: path.resolve(__dirname, "./tsconfig.json"),
              transpileOnly: true, // Speed up compilation
            },
          },
        ],
      },
      {
        test: /\.(js|jsx)$/,
        exclude: /node_modules/,
        use: {
          loader: "babel-loader",
          options: {
            presets: [
              ["@babel/preset-env", {
                targets: {
                  browsers: ["> 1%", "last 2 versions", "not ie <= 8"]
                },
                modules: false,
                useBuiltIns: "usage",
                corejs: 3
              }],
              ["@babel/preset-react", {
                runtime: "automatic"
              }]
            ],
            plugins: [
              "@babel/plugin-transform-class-properties",
              "@babel/plugin-transform-object-rest-spread",
              "@babel/plugin-syntax-dynamic-import",
              ["@babel/plugin-transform-runtime", {
                corejs: false,
                helpers: true,
                regenerator: true,
                useESModules: false
              }]
            ]
          }
        },
      },
      {
        test: /\.(png|svg|jpg|jpeg|gif|ico)$/i,
        type: 'asset/resource',
        generator: {
          filename: 'images/[name][ext]'
        }
      },
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader', 'postcss-loader']
      },
      {
        test: /\.mjs$/,
        include: /node_modules/,
        type: 'javascript/auto'
      }
    ],
  },
  resolve: {
    extensions: ['.js', '.jsx', '.ts', '.tsx', '.mjs'],
    modules: [path.resolve(__dirname, "src"), "node_modules"],
    alias: {
      '@emotion/react': require.resolve('@emotion/react'),
      '@emotion/styled': require.resolve('@emotion/styled'),
      '@emotion/is-prop-valid': require.resolve('@emotion/is-prop-valid'),
      'process/browser': require.resolve('process/browser'),
    },
    fallback: {
      "path": require.resolve("path-browserify"),
      "crypto": require.resolve("crypto-browserify"),
      "stream": require.resolve("stream-browserify"),
      "buffer": require.resolve("buffer"),
      "util": require.resolve("util"),
      "url": require.resolve("url"),
      "querystring": require.resolve("querystring-es3"),
      "fs": false,
      "net": false,
      "tls": false,
      "https": require.resolve("https-browserify"),
      "http": false,
      "os": require.resolve("os-browserify/browser"),
      "assert": require.resolve("assert"),
      "constants": require.resolve("constants-browserify"),
      "child_process": false,
      "worker_threads": false,
      "process": require.resolve("process/browser")
    }
  },
  optimization: {
    minimize: process.env.NODE_ENV === 'production',
    // Completely disable code splitting to ensure single main.js
    splitChunks: false,
    // Ensure proper module concatenation
    concatenateModules: true,
    // Disable runtime chunk
    runtimeChunk: false,
    // Remove empty chunks
    removeEmptyChunks: true,
    // Ensure deterministic chunk names
    chunkIds: 'deterministic',
  },
  plugins: [
    new NodeProtocolPlugin(),
    new RemoveEmptyChunksPlugin(),
    new webpack.DefinePlugin({
      'process.env.NODE_ENV': JSON.stringify(process.env.NODE_ENV || "development"),
      'process.env.CLOUD_API_URL': JSON.stringify(process.env.CLOUD_API_URL || 'https://cognitio-cloud-api.onrender.com/api/v1')
    }),
    new webpack.ProvidePlugin({
      Buffer: ['buffer', 'Buffer'],
      process: 'process/browser',
    }),
  ],
  watchOptions: {
    ignored: /node_modules/,
    poll: 1000,
  },
  devServer: {
    static: {
      directory: path.join(__dirname, '../static'),
    },
    hot: true,
    port: 3000,
    proxy: {
      '/api': 'http://localhost:3927',
      '/static': 'http://localhost:3927'
    },
    historyApiFallback: true,
  },
  performance: {
    hints: process.env.NODE_ENV === 'production' ? 'warning' : false,
    maxEntrypointSize: 10000000, // 10MB - increased for single bundle
    maxAssetSize: 10000000
  },
};