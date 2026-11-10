# Ravedio chat crop review

In the Development app, open Settings → Developer tools → Sample screens →
Messages, then open Unverified channel 1. Switch between **Standard**,
**Current crop**, and **Tighter crop** in place. The selector appears when the
verified portrait bundle is included.

The same eight senders repeat at 24 pt on iOS and 24 dp on Android. Standard
calls the existing sprite renderer with sample profiles. The sprites use Side
part as the closest match to Flow and Full beard for both beard lengths. The
two portrait modes use the same artwork per sender, with only the framing
changed. The current crop is the original 120 px export. The tighter crop
reframes the 384 px Blender render and keeps the 15° camera and cool-white
background. The square becomes 324 px before resampling, making the avatar
about 19% larger. This package contains fixed portraits for the test.

## Stage the comparison

Extract `ravedio-chat-crop-323.zip` and set
`RAVEDIO_AVATAR_R323_CHAT_REVIEW` to the directory containing
`mobile-portraits.json` in the mobile checkout with the 323 sample code.
Keep this environment variable set through project generation and build.

- Android from the mobile repository root: `apps/android/gradlew -p apps/android -PavatarLab=true :app:assembleDevelopmentDebug`.
- iOS on a Mac: run `python3 tools/avatar-proof/native.py ios-build` to stage the resources and generate the project. Then build and run the `RavedioDevelopment` scheme on the phone using Xcode.

## On both phones

Open the same chat in each mode. Check whether the portrait makes it easier
to spot a change of sender while scanning, including the deeper skin tones.
Check the beard and eyes with the phone at normal reading distance. Compare
the same scroll with a cold app start and again with the images already
loaded. For a decision on scroll performance, record frame timing and memory
on a lower-end phone. This sample loads eight fixed portraits and does not
exercise first-time composition for arbitrary profiles.
