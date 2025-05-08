# React + TypeScript + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## Expanding the ESLint configuration

If you are developing a production application, we recommend updating the configuration to enable type-aware lint rules:

```js
export default tseslint.config({
  extends: [
    // Remove ...tseslint.configs.recommended and replace with this
    ...tseslint.configs.recommendedTypeChecked,
    // Alternatively, use this for stricter rules
    ...tseslint.configs.strictTypeChecked,
    // Optionally, add this for stylistic rules
    ...tseslint.configs.stylisticTypeChecked,
  ],
  languageOptions: {
    // other options...
    parserOptions: {
      project: ["./tsconfig.node.json", "./tsconfig.app.json"],
      tsconfigRootDir: import.meta.dirname,
    },
  },
});
```

You can also install [eslint-plugin-react-x](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-x) and [eslint-plugin-react-dom](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-dom) for React-specific lint rules:

```js
// eslint.config.js
import reactX from "eslint-plugin-react-x";
import reactDom from "eslint-plugin-react-dom";

export default tseslint.config({
  plugins: {
    // Add the react-x and react-dom plugins
    "react-x": reactX,
    "react-dom": reactDom,
  },
  rules: {
    // other rules...
    // Enable its recommended typescript rules
    ...reactX.configs["recommended-typescript"].rules,
    ...reactDom.configs.recommended.rules,
  },
});
```

## Firebase Setup

To connect the frontend to Firebase for authentication and other services, you need to configure your Firebase project credentials.

1.  **Create or Access your Firebase Project:**

    - Go to the [Firebase Console](https://console.firebase.google.com/).
    - Select your existing project or create a new one.
    - Ensure you have enabled the necessary authentication methods (e.g., Email/Password, Google Sign-In) in the "Authentication" > "Sign-in method" tab.

2.  **Get Firebase SDK Configuration:**

    - In your Firebase project dashboard, navigate to "Project settings" (click the gear icon next to "Project Overview").
    - Scroll down to the "Your apps" section.
    - If you haven't added a web app yet, click the Web icon (`</>`) to register a new web app. Give it a nickname (e.g., "Frontend App").
    - Once your web app is registered, find the "Firebase SDK snippet" section and select the "Config" option (it might also be labeled "npm" or "Use a module bundler").
    - You will see a `firebaseConfig` object. This object contains the keys and IDs needed for the next step.

3.  **Configure Environment Variables:**

    - In the root of the `frontend /frontend` directory, create a file named `.env` if it doesn't already exist.
    - Add the following environment variables to your `.env` file, replacing the placeholder values with the actual values from your `firebaseConfig` object:

      ```env
      VITE_FIREBASE_API_KEY="YOUR_API_KEY"
      VITE_FIREBASE_AUTH_DOMAIN="YOUR_AUTH_DOMAIN"
      VITE_FIREBASE_PROJECT_ID="YOUR_PROJECT_ID"
      VITE_FIREBASE_STORAGE_BUCKET="YOUR_STORAGE_BUCKET"
      VITE_FIREBASE_MESSAGING_SENDER_ID="YOUR_MESSAGING_SENDER_ID"
      VITE_FIREBASE_APP_ID="YOUR_APP_ID"
      ```

    - Refer to the `frontend /frontend/.env.example` file for the required variable names.

4.  **Install Dependencies:**
    - Ensure you have installed the `firebase` package:
      ```bash
      npm install firebase
      # or
      # yarn add firebase
      ```

After these steps, your frontend application should be able to initialize Firebase using these environment variables.
