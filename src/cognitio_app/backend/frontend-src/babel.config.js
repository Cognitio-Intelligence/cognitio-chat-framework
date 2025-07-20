module.exports = {
  presets: [
    [
      "@babel/preset-env",
      {
        targets: {
          browsers: ["> 1%", "last 2 versions", "not ie <= 8"]
        },
        modules: false,
        useBuiltIns: "usage",
        corejs: 3
      }
    ],
    [
      "@babel/preset-react",
      {
        runtime: "automatic"
      }
    ],
    "@babel/preset-typescript"
  ],
  plugins: [
    "@babel/plugin-transform-class-properties",
    "@babel/plugin-transform-object-rest-spread",
    "@babel/plugin-syntax-dynamic-import",
    [
      "@babel/plugin-transform-runtime",
      {
        corejs: false,
        helpers: true,
        regenerator: true,
        useESModules: false
      }
    ]
  ].filter(Boolean),
  env: {
    development: {
      plugins: [
        "react-refresh/babel"
      ]
    },
    production: {
      plugins: []
    }
  }
}; 