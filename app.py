import streamlit as st
import os
import glob
import subprocess
from pydub import AudioSegment
import yt_dlp
import shutil

# --- Configurazione della Pagina Streamlit ---
st.set_page_config(
    page_title="AI Audio Mixer",
    page_icon="🎧",
    layout="centered",
)

# --- Funzione di Elaborazione Principale ---
@st.cache_data(show_spinner=False) # Spinner gestito manualmente
def process_and_mix(yt_url, mix_type):
    # Directory unica per evitare conflitti tra esecuzioni simultanee
    BASE_DIR = f"temp_processing_{hash(yt_url)}_{mix_type}" 
    INPUT_DIR = os.path.join(BASE_DIR, "input")
    SEPARATED_DIR = os.path.join(BASE_DIR, "separated")
    OUTPUT_DIR = "output"
    
    if os.path.exists(BASE_DIR):
        shutil.rmtree(BASE_DIR)
    os.makedirs(INPUT_DIR, exist_ok=True)
    os.makedirs(SEPARATED_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
        
    try:
        progress_bar = st.progress(0, text="Starting process...")

        # --- 1. Download ---
        progress_bar.progress(10, text="⬇️ Downloading audio from YouTube...")
        input_audio_path = os.path.join(INPUT_DIR, "input_audio.mp3")
        ydl_opts = {
            'format': 'bestaudio/best', 'outtmpl': input_audio_path, 'noplaylist': True,
            'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'}],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([yt_url])
        
        # --- 2. Separazione ---
        progress_bar.progress(30, text="🎶 Separating stems with Demucs... (this can take several minutes)")
        command = f'python -m demucs.separate -n htdemucs --mp3 "{input_audio_path}" -o "{SEPARATED_DIR}"'
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        
        htdemucs_output_dir = os.path.join(SEPARATED_DIR, "htdemucs")
        song_folder_name = os.listdir(htdemucs_output_dir)[0]
        tracks_path = os.path.join(htdemucs_output_dir, song_folder_name)
        separated_tracks = glob.glob(os.path.join(tracks_path, "*.mp3"))
        
        if not separated_tracks:
            raise Exception("Demucs failed to separate any tracks.")
            
        # --- 3. Mixaggio ---
        progress_bar.progress(80, text=f"🎛️ Creating '{mix_type}' mix...")
        tracks_to_mix = []
        if mix_type == "Karaoke (no vocals)":
            tracks_to_mix = [t for t in separated_tracks if "vocals" not in os.path.basename(t)]
        elif mix_type == "Drumless":
            tracks_to_mix = [t for t in separated_tracks if "drums" not in os.path.basename(t)]
        elif mix_type == "Drums only":
            tracks_to_mix = [t for t in separated_tracks if "drums" in os.path.basename(t)]
            
        if not tracks_to_mix:
             raise Exception(f"Could not create the mix. No suitable tracks found.")

        if len(tracks_to_mix) == 1:
            final_mix = AudioSegment.from_mp3(tracks_to_mix[0])
        else:
            final_mix = AudioSegment.from_mp3(tracks_to_mix[0])
            for track_file in tracks_to_mix[1:]:
                final_mix = final_mix.overlay(AudioSegment.from_mp3(track_file))
        
        # --- 4. Esportazione ---
        progress_bar.progress(95, text="✅ Finalizing the file...")
        mix_type_fn = mix_type.lower().replace(' ', '_').replace('(', '').replace(')', '')
        output_filename = f"final_mix_{mix_type_fn}.mp3"
        final_output_path = os.path.join(OUTPUT_DIR, output_filename)
        final_mix.export(final_output_path, format="mp3")
        
        shutil.rmtree(BASE_DIR)
        progress_bar.progress(100, text="Complete!")
        progress_bar.empty()
        return final_output_path

    except subprocess.CalledProcessError as e:
        st.error(f"An error occurred during audio processing. Demucs failed.")
        st.code(f"Error details:\n{e.stderr}")
        if os.path.exists(BASE_DIR):
            shutil.rmtree(BASE_DIR)
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        if os.path.exists(BASE_DIR):
            shutil.rmtree(BASE_DIR)
        return None

# --- Interfaccia Utente (UI) ---
st.title("🎧 AI Audio Mixer")
st.markdown("Paste a YouTube link, choose a mix type, and I'll create a custom audio track for you.")

url = st.text_input("YouTube Link", placeholder="https://www.youtube.com/watch?v=...")
mix_type = st.radio("Select Mix Type", ["Karaoke (no vocals)", "Drumless", "Drums only"], horizontal=True)

if st.button("Generate Mix", type="primary"):
    if url:
        result_path = process_and_mix(url, mix_type)
        if result_path and os.path.exists(result_path):
            st.success("🎉 Mix complete!")
            st.audio(result_path)
            with open(result_path, "rb") as file:
                st.download_button("Download MP3", file, os.path.basename(result_path), "audio/mpeg")
    else:
        st.warning("Please enter a YouTube URL.")