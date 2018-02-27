using SixLabors.ImageSharp;

namespace Rendering
{
    class Program
    {
        static void Main(string[] args)
        {
            using (Image<Rgba32> image = Image.Load(args[0]))
            {
                image.Mutate(x => x
                    .OilPaint()
                    .Grayscale());
                image.Save($"new_{args[0]}");
            }
        }
    }
}
