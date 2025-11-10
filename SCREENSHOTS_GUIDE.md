# 📸 Guide: Adding Screenshots to GitHub

This guide will help you add beautiful screenshots to your GitHub repository.

## Step-by-Step Instructions

### 1. Create Screenshots Folder

Create a `screenshots` folder in the root directory of your project:

```bash
mkdir screenshots
```

### 2. Take Screenshots

Take screenshots of your application. Here are some recommended screenshots:

- **Main Page** (`main-page.png`) - The home page with the URL input form
- **History Page** (`history-page.png`) - The video history page
- **Authentication Modal** (`auth-modal.png`) - The login/register modal
- **Video History** (`video-history.png`) - The history page with video cards
- **Transcript View** (`transcript-view.png`) - Expanded transcript view
- **Summarization Result** (`summary-result.png`) - A summary result page

### 3. Optimize Screenshots

For best results on GitHub:

- **Format**: Use PNG for screenshots (better quality) or JPG (smaller file size)
- **Size**: Keep file sizes reasonable (under 1MB per image)
- **Dimensions**: Recommended width: 1200-1920px
- **Tools**: You can use tools like:
  - [TinyPNG](https://tinypng.com/) - Compress PNG images
  - [Squoosh](https://squoosh.app/) - Optimize images
  - [ImageOptim](https://imageoptim.com/) - Mac tool for optimization

### 4. Add Screenshots to Repository

Add your screenshots to the `screenshots` folder:

```bash
# Copy your screenshots to the screenshots folder
cp ~/Desktop/main-page.png screenshots/
cp ~/Desktop/history-page.png screenshots/
# etc.
```

### 5. Update README.md

Open `README.md` and replace the screenshot section with your images:

```markdown
## 📸 Screenshots

![Main Page](screenshots/main-page.png)
*The main page with URL input form*

![History Page](screenshots/history-page.png)
*Video history page showing all summarized videos*

![Authentication Modal](screenshots/auth-modal.png)
*Login and registration modal*

![Video History](screenshots/video-history.png)
*Detailed view of video cards with transcripts*

![Transcript View](screenshots/transcript-view.png)
*Expanded transcript view with copy functionality*
```

### 6. Commit and Push

Commit your screenshots:

```bash
git add screenshots/
git add README.md
git commit -m "Add screenshots to README"
git push origin main
```

## Tips for Beautiful Screenshots

### 1. Use Consistent Browser Window Size

Take all screenshots with the same browser window size for consistency.

### 2. Hide Personal Information

Make sure to hide or blur any personal information, API keys, or sensitive data.

### 3. Use Browser DevTools

- Use browser DevTools to hide browser UI (F12 → Toggle device toolbar)
- Use responsive design mode to show mobile views
- Take screenshots at different breakpoints (desktop, tablet, mobile)

### 4. Add Annotations (Optional)

You can add annotations using tools like:
- [Annotely](https://annotely.com/) - Add arrows and text
- [Skitch](https://evernote.com/products/skitch) - Annotation tool
- [Monosnap](https://monosnap.com/) - Screenshot and annotation

### 5. Create a Screenshot Gallery

For multiple screenshots, you can create a nice gallery layout:

```markdown
## 📸 Screenshots

<div align="center">
  <img src="screenshots/main-page.png" width="45%" />
  <img src="screenshots/history-page.png" width="45%" />
</div>

<div align="center">
  <img src="screenshots/auth-modal.png" width="45%" />
  <img src="screenshots/video-history.png" width="45%" />
</div>
```

### 6. Use GitHub's Image CDN

GitHub automatically serves images through their CDN, so you don't need to worry about hosting.

## Alternative: Using GitHub Issues for Screenshots

If you want to test screenshots before adding them to README:

1. Create a GitHub Issue
2. Drag and drop screenshots into the issue
3. GitHub will create a URL for each image
4. Copy the URLs and use them in your README

## Example README Section

Here's a complete example of a beautiful screenshot section:

```markdown
## 📸 Screenshots

### Main Features

<div align="center">
  <h3>Main Page</h3>
  <img src="screenshots/main-page.png" alt="Main Page" width="800"/>
  <p><em>The main page with URL input form for summarizing YouTube videos</em></p>
</div>

<div align="center">
  <h3>Video History</h3>
  <img src="screenshots/history-page.png" alt="History Page" width="800"/>
  <p><em>View all your summarized videos with thumbnails and transcripts</em></p>
</div>

<div align="center">
  <h3>Authentication</h3>
  <img src="screenshots/auth-modal.png" alt="Auth Modal" width="600"/>
  <p><em>Secure login and registration with JWT authentication</em></p>
</div>
```

## Troubleshooting

### Images Not Showing

- Make sure the file path is correct (relative to README.md)
- Check that images are committed to the repository
- Verify file extensions are lowercase (.png, not .PNG)

### Images Too Large

- Compress images using tools mentioned above
- Consider using JPG format for photos
- Use PNG only when you need transparency

### Images Not Centered

- Use HTML `<div align="center">` tags for centering
- Or use markdown with HTML: `<img src="..." align="center" />`

## Best Practices

1. **Keep it updated**: Update screenshots when UI changes
2. **Show key features**: Focus on main features, not every detail
3. **Be consistent**: Use same browser, same window size
4. **Optimize**: Compress images to keep repository size small
5. **Accessibility**: Add alt text to all images

---

Happy screenshotting! 📸✨

